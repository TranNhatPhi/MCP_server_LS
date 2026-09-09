"""F1 · Cổng điều phối — điểm vào duy nhất cho mọi lệnh gọi.

Chạy được cả hai chế độ theo chuẩn kỹ thuật chương 15:
    python -m lsth_mcp                      # stdio, cho Claude Desktop trên máy cá nhân
    python -m lsth_mcp --transport http     # HTTP, cho máy chủ nội bộ

Mọi tool ở đây đều trả về khung chuẩn {ok, data, sources[], warnings[], error} và
đều đi qua nhật ký sáu trường. Không tool nào gửi mail, đặt hàng hay đẩy dữ liệu
ra ngoài công ty — nguyên tắc 1 "Máy soạn nháp, người bấm nút".
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.audit import AuditLog, audited
from .core.config import get_settings
from .core.envelope import fail, ok
from .core.errors import LsthError
from .core.permissions import WriteGateStore
from .domain.identity import IdentityMap
from .domain.templates import TemplateStore
from .io.discovery import build_tree, search_files
from .io.registry import list_files, read_any
from .io.writers.excel import write_rows
from .io.writers.safe import SafeWriter
from .io.writers.structured import write_csv, write_json
from .servers import ALL_SPECS, FOUNDATION
from .servers.s1_techpack import TechpackServer

SERVER_NAME = "lsth-mcp"
VERSION = "0.1.0"


def _audit() -> AuditLog:
    cfg = get_settings()
    return AuditLog(cfg.audit_dir, cfg.audit_retention_days)


def _guard(tool: str, params: Dict[str, Any], fn):
    """Bọc một tool ở tầng cổng: ghi nhật ký, đổi lỗi thành envelope."""
    cfg = get_settings()
    try:
        with audited(_audit(), f"{SERVER_NAME}.{tool}", params,
                     actor=cfg.actor, role=cfg.role) as trace:
            return fn(trace)
    except LsthError as exc:
        return fail(exc)
    except Exception as exc:  # noqa: BLE001
        return fail(exc)


# --------------------------------------------------------------------------- đọc

def file_list(pattern: str = "**/*", root: Optional[str] = None,
              limit: int = 200) -> Dict[str, Any]:
    """Liệt kê file trong vùng dữ liệu cho phép."""
    def run(_trace):
        files = list_files(pattern, root=root, limit=limit)
        return ok({"files": files, "count": len(files)})
    return _guard("file_list", {"pattern": pattern, "root": root, "limit": limit}, run)


def file_search(query: str, root: Optional[str] = None, limit: int = 50,
                scan_limit: int = 10000) -> Dict[str, Any]:
    """Tìm file theo tên/đường dẫn, không phân biệt hoa thường và dấu tiếng Việt.

    root: tên vùng (raw, work...), URI s3://lsth-raw/thư-mục/ hoặc thư mục local.
    Mọi từ trong query phải có trong đường dẫn, ví dụ 'S2749189 BOM' hoặc 'cong viec'.
    Chỉ tìm metadata, không tìm nội dung file.
    Tối đa scan_limit file được xét; truncated=true nghĩa là kết quả chưa đầy đủ.
    """
    def run(_trace):
        data = search_files(query, root=root, limit=limit, scan_limit=scan_limit)
        return ok(data, sources=[{"file": f["path"]} for f in data["files"]],
                  warnings=["Kết quả chưa đầy đủ: tăng limit/scan_limit hoặc thu hẹp root."]
                  if data["truncated"] else [])
    return _guard("file_search", {"query": query, "root": root, "limit": limit,
                                  "scan_limit": scan_limit}, run)


def file_tree(root: Optional[str] = None, max_depth: int = 4, limit: int = 200,
              scan_limit: int = 10000, query: Optional[str] = None) -> Dict[str, Any]:
    """Tìm trong cây thư mục MinIO/S3 hoặc local; trả tree JSON và tree_text dễ đọc.

    root: tên vùng, URI s3://lsth-raw/thư-mục/ hoặc thư mục local.
    query: mã hàng, tên file/thư mục hoặc đuôi file; khớp mọi từ, không phân biệt dấu
    tiếng Việt và hoa thường. Ví dụ query='S2749189 BOM', root='s3://lsth-raw/'.
    Giữ nhánh cha của file khớp; bỏ query để hiện toàn cây. Không gồm thư mục rỗng.
    limit giới hạn số file; max_depth tính từ root, thư mục sâu hơn có collapsed=true.
    matched_count là số file khớp trong phần đã quét; scan_truncated=true nghĩa là chưa quét hết.
    """
    def run(_trace):
        data = build_tree(root=root, max_depth=max_depth, limit=limit,
                          scan_limit=scan_limit, query=query)
        sources = data.pop("sources")
        warnings = []
        if data["truncated"]:
            warnings.append("Cây chưa đầy đủ: tăng limit/scan_limit hoặc thu hẹp root.")
        if data["depth_limited"]:
            warnings.append("Một số thư mục được thu gọn; tăng max_depth hoặc chọn root sâu hơn.")
        return ok(data, sources=sources, warnings=warnings)
    return _guard("file_tree", {"root": root, "max_depth": max_depth,
                                "limit": limit, "scan_limit": scan_limit, "query": query}, run)


def file_read(path: str, sheet: Optional[str] = None, pages: Optional[List[int]] = None,
              limit: Optional[int] = None) -> Dict[str, Any]:
    """Đọc bất kỳ file nào được hỗ trợ: xlsx, pdf, csv, json, docx, txt."""
    def run(trace):
        kwargs: Dict[str, Any] = {}
        if sheet:
            kwargs["sheet"] = sheet
        if pages:
            kwargs["pages"] = pages
        if limit:
            kwargs["limit"] = limit
        result = read_any(path, trace=trace, **kwargs)
        return ok(result.to_dict(), sources=result.sources[:1] + result.sources[-1:],
                  warnings=result.warnings)
    return _guard("file_read", {"path": path, "sheet": sheet, "pages": pages}, run)


def excel_sheets(path: str) -> Dict[str, Any]:
    """Liệt kê sheet của một file Excel trước khi quyết định đọc sheet nào."""
    def run(trace):
        from .core.paths import resolve_within
        from .io.readers.excel import ExcelReader
        cfg = get_settings()
        target = resolve_within(path, cfg.read_roots, must_exist=True)
        trace.read(target)
        names = ExcelReader().sheet_names(target)
        return ok({"sheets": names, "count": len(names)},
                  sources=[{"file": str(target)}])
    return _guard("excel_sheets", {"path": path}, run)


# --------------------------------------------------------------------------- ghi

def file_write(path: str, content: str, server: str = "gateway",
               dry_run: bool = False) -> Dict[str, Any]:
    """Ghi file chữ vào data/work hoặc data/out. Đi qua cổng quyền ghi."""
    def run(trace):
        writer = SafeWriter.for_server(server, trace=trace, dry_run=dry_run)
        result = writer.write_text(path, content)
        return ok(result.to_dict(), sources=[result.source] if result.source else None)
    return _guard("file_write", {"path": path, "server": server,
                                 "content": content, "dry_run": dry_run}, run)


def excel_write(path: str, rows: List[Dict[str, Any]], sheet_name: str = "Data",
                server: str = "gateway", draft_banner: bool = True,
                dry_run: bool = False) -> Dict[str, Any]:
    """Xuất bảng ra Excel. Mặc định đóng dấu 'BẢN NHÁP DO MÁY DỰNG' ở dòng đầu."""
    def run(trace):
        writer = SafeWriter.for_server(server, trace=trace, dry_run=dry_run)
        result = write_rows(writer, path, rows, sheet_name=sheet_name,
                            draft_banner=draft_banner)
        return ok(result.to_dict(), sources=[result.source] if result.source else None)
    return _guard("excel_write", {"path": path, "rows": rows, "server": server}, run)


def json_write(path: str, data: Any, server: str = "gateway",
               dry_run: bool = False) -> Dict[str, Any]:
    """Ghi JSON — định dạng trao đổi giữa các server theo hợp đồng F2."""
    def run(trace):
        writer = SafeWriter.for_server(server, trace=trace, dry_run=dry_run)
        result = write_json(writer, path, data)
        return ok(result.to_dict(), sources=[result.source] if result.source else None)
    return _guard("json_write", {"path": path, "server": server}, run)


def csv_write(path: str, rows: List[Dict[str, Any]], server: str = "gateway",
              dry_run: bool = False) -> Dict[str, Any]:
    """Xuất CSV (utf-8-sig, mở bằng Excel không vỡ dấu tiếng Việt)."""
    def run(trace):
        writer = SafeWriter.for_server(server, trace=trace, dry_run=dry_run)
        result = write_csv(writer, path, rows)
        return ok(result.to_dict(), sources=[result.source] if result.source else None)
    return _guard("csv_write", {"path": path, "server": server}, run)


# --------------------------------------------------------- nền tảng và nghiệp vụ

def identity_resolve(value: str, from_system: str, to_system: str,
                     market: Optional[str] = None,
                     customer: Optional[str] = None) -> Dict[str, Any]:
    """F3 — đổi mã giữa các hệ: LS-style ↔ style khách ↔ UPC ↔ mã vật tư."""
    def run(trace):
        cfg = get_settings()
        path = cfg.identity_dir / "identity_map.csv"
        trace.read(path)
        answer = IdentityMap.load(path).resolve(
            value, from_system=from_system, to_system=to_system,
            market=market, customer=customer)
        return ok(answer, sources=[answer["source"]] if answer.get("source") else None)
    return _guard("identity_resolve",
                  {"value": value, "from_system": from_system, "to_system": to_system}, run)


def template_get(kind: str, customer: Optional[str] = None,
                 market: Optional[str] = None) -> Dict[str, Any]:
    """F4 — lấy file khuôn đã duyệt cho một loại tài liệu."""
    def run(trace):
        cfg = get_settings()
        store = TemplateStore.load(cfg.templates_dir)
        template = store.get(kind, customer=customer, market=market)
        trace.read(template.file)
        return ok({
            "kind": template.kind, "file": str(template.file),
            "customer": template.customer, "naming": template.naming,
            "approved_by": template.approved_by, "approved_at": template.approved_at,
            "cell_map": template.cell_map,
        }, sources=[template.source])
    return _guard("template_get", {"kind": kind, "customer": customer}, run)


def techpack_parse(file: str, max_pages: Optional[int] = None) -> Dict[str, Any]:
    """S1 — bóc tech pack PDF ra thực thể Style."""
    return TechpackServer().techpack_parse(file, max_pages=max_pages)


def bom_extract(file: str, sheet: Optional[str] = None,
                limit: Optional[int] = None) -> Dict[str, Any]:
    """S1 — bóc BOM xlsx ra BomLine[] theo hợp đồng dữ liệu F2."""
    return TechpackServer().bom_extract(file, sheet=sheet, limit=limit)


def bom_diff(techpack_file: str, bom_file: str,
             bom_sheet: Optional[str] = None) -> Dict[str, Any]:
    """S1 — so tech pack với BOM, báo mâu thuẫn chứ không tự chọn (nguyên tắc 3)."""
    return TechpackServer().diff_check(techpack_file, bom_file, bom_sheet=bom_sheet)


# ------------------------------------------------------------------ vận hành

def program_status() -> Dict[str, Any]:
    """Bức tranh 17 thành phần: cái nào đã dựng, cái nào đang chờ lấp khoảng trống."""
    def run(_trace):
        cfg = get_settings()
        gates = WriteGateStore(cfg.state_dir / "write_gates.json")
        servers = []
        for spec in ALL_SPECS:
            gate = gates.get(spec.module)
            servers.append({
                "code": spec.code, "name": spec.name, "round": spec.round,
                "priority": spec.priority, "blocked_by": spec.blocked_by,
                "write_unlocked": gate.unlocked,
                "validated_styles": len(gate.validated_styles),
            })
        return ok({
            "version": VERSION,
            "write_enabled": cfg.write_enabled,
            "foundation": FOUNDATION,
            "servers": servers,
            "total_components": len(FOUNDATION) + len(ALL_SPECS),
        })
    return _guard("program_status", {}, run)


def audit_tail(limit: int = 20) -> Dict[str, Any]:
    """Chương 11 — xem lệnh gọi gần nhất: ai gọi, lúc nào, đọc file nào, kết quả sao."""
    def run(_trace):
        rows = _audit().tail(limit)
        return ok({"records": rows, "count": len(rows)})
    return _guard("audit_tail", {"limit": limit}, run)


#: Bảng tool đăng ký với MCP. Tên theo mẫu danh_từ + động_từ (chuẩn chương 15).
TOOLS = [
    file_list, file_search, file_tree, file_read, excel_sheets,
    file_write, excel_write, json_write, csv_write,
    identity_resolve, template_get,
    techpack_parse, bom_extract, bom_diff,
    program_status, audit_tail,
]


def build_app(name: str = SERVER_NAME):
    """Dựng ứng dụng MCP. Thiếu SDK thì báo cách cài, không làm hỏng cả gói."""
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "Chưa cài MCP SDK.\n"
            "  pip install 'mcp>=2.0'\n"
            "Lưu ý: SDK cần Python 3.10 trở lên. Riêng lớp đọc/ghi (lsth_mcp.io) "
            "chạy được trên Python 3.9 mà không cần SDK."
        ) from exc

    get_settings().ensure_dirs()
    app = MCPServer(
        name,
        title="LSTH — Giảm workload khối BU",
        version=VERSION,
        instructions=(
            "Công cụ đọc dữ liệu sản xuất của Lucky Star LSTH: tech pack PDF, BOM Excel, "
            "file khảo sát, bảng ánh xạ mã hàng.\n\n"
            "Ba điều cần nhớ khi dùng:\n"
            "1. Mọi kết quả đều kèm trường `sources` nói rõ lấy từ file/sheet/dòng nào. "
            "Khi trả lời người dùng, hãy dẫn lại nguồn đó.\n"
            "2. Máy chỉ soạn nháp. Không tool nào gửi mail, đặt hàng hay đẩy dữ liệu ra "
            "ngoài công ty.\n"
            "3. Tool không đoán. Gặp dữ liệu thiếu thì nó báo lỗi kèm hướng dẫn ở "
            "`error.hint` — hãy đọc và làm theo, đừng tự suy ra giá trị thay nó."
        ),
    )
    for tool in TOOLS:
        app.tool(name=tool.__name__, description=(tool.__doc__ or "").strip())(tool)
    return app


#: Giao diện thêm connector của Claude/Cowork chỉ nhận URL và (tuỳ chọn) OAuth
#: Client ID/Secret — KHÔNG cho nhập header tuỳ ý. Nên bí mật phải nằm trong chính
#: đường dẫn: server gắn endpoint ở /mcp/<token>. Ai không biết token thì router
#: trả 404, không chạm được tới tool nào.
#:
#: Đây là mức đủ cho một buổi thử trên dữ liệu giả. Khi đưa vào dùng thật với dữ
#: liệu khách, phải thay bằng OAuth (MCPServer nhận auth_server_provider /
#: token_verifier) — xem docs/DEPLOY.md.
def mcp_path_for(token: str) -> str:
    return f"/mcp/{token}" if token else "/mcp"


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="lsth-mcp", description=__doc__)
    parser.add_argument("--transport", choices=("stdio", "http"), default=None,
                        help="stdio cho máy cá nhân, http cho máy chủ nội bộ")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--public-host", default=None,
                        help="Tên miền công khai (tunnel/reverse proxy) để cho qua Host header")
    parser.add_argument("--status", action="store_true",
                        help="In bức tranh 17 thành phần rồi thoát, không chạy server")
    parser.add_argument("--list-tools", action="store_true",
                        help="In danh sách tool rồi thoát")
    args = parser.parse_args(argv)

    cfg = get_settings()
    if args.status:
        import json
        print(json.dumps(program_status(), ensure_ascii=False, indent=2))
        return 0
    if args.list_tools:
        for tool in TOOLS:
            print(f"{tool.__name__:<18} {(tool.__doc__ or '').strip().splitlines()[0]}")
        return 0

    app = build_app()
    transport = args.transport or cfg.transport
    if transport != "http":
        app.run(transport="stdio")
        return 0

    import os

    host = args.host or cfg.http_host
    port = args.port or cfg.http_port

    # Host header hợp lệ: localhost để thử tại chỗ, cộng tên miền công khai nếu có.
    allowed_hosts = ["127.0.0.1", "localhost", f"127.0.0.1:{port}",
                     f"localhost:{port}", f"{host}:{port}"]
    public_host = args.public_host or os.environ.get("LSTH_PUBLIC_HOST", "")
    if public_host:
        allowed_hosts += [public_host, f"https://{public_host}"]

    import uvicorn
    from mcp.server.transport_security import TransportSecuritySettings
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    token = os.environ.get("LSTH_MCP_TOKEN", "")
    mcp_path = mcp_path_for(token)

    http_app = app.streamable_http_app(
        streamable_http_path=mcp_path,
        # Mô hình không trạng thái theo bản cập nhật spec 2026-07-28 — hợp với
        # việc Claude gọi từ đám mây, mỗi lệnh một request độc lập.
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(allowed_hosts=allowed_hosts),
        host=host,
    )

    async def health(_request):
        """Để kiểm tra tunnel còn sống mà không cần token."""
        return JSONResponse({
            "ok": True, "server": SERVER_NAME, "version": VERSION,
            "tools": len(TOOLS), "write_enabled": cfg.write_enabled,
        })

    http_app.router.routes.append(Route("/health", health, methods=["GET"]))

    if token:
        print(f"[lsth-mcp] Endpoint đặt sau token bí mật ({len(token)} ký tự trong đường dẫn).")
    elif public_host:
        print("[lsth-mcp] CẢNH BÁO: mở ra internet mà KHÔNG có LSTH_MCP_TOKEN — "
              "bất kỳ ai biết URL đều gọi được.")

    print(f"[lsth-mcp] v{VERSION} · streamable-http · http://{host}:{port}{mcp_path}")
    print(f"[lsth-mcp] Chế độ ghi: {'MỞ' if cfg.write_enabled else 'ĐÓNG (chỉ đọc)'}"
          f" · vai trò: {cfg.role} · {len(TOOLS)} tool")
    if public_host:
        print(f"[lsth-mcp] URL công khai: https://{public_host}{mcp_path}")

    uvicorn.run(http_app, host=host, port=port, log_level="info")
    return 0
