"""Tìm tên file và xem cây dữ liệu bằng metadata, không đọc nội dung file."""
from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config import Settings, get_settings
from ..core.errors import PathOutsideRootError, ValidationError
from ..core.paths import resolve_within
from .registry import SUPPORTED, list_files
from .storage import BUCKETS, SEARCH_ORDER, check_key, get_store, using_minio


def _bounded(value: int, name: str, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValidationError(
            f"{name} phải từ 1 đến {maximum}.",
            hint=f"Truyền số nguyên dương không vượt quá {maximum}.",
        )


def _search_text(value: str) -> str:
    """Khớp tên tiếng Việt có/không dấu, kể cả Unicode tách dấu của macOS."""
    normalized = unicodedata.normalize("NFD", value.casefold()).replace("đ", "d")
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _matches_query(path: str, query: str) -> bool:
    haystack = _search_text(path)
    return all(word in haystack for word in _search_text(query).split())


def _inventory(root: Optional[str], settings: Settings, scan_limit: int):
    prefix = ""
    local_roots = {name: getattr(settings, name + "_dir") for name in
                   ("raw", "work", "out", "templates", "identity", "eval")}
    minio = using_minio(settings) or bool(root and root.startswith("s3://"))
    if minio:
        area = root
        if root and root.startswith("s3://"):
            bucket, _, prefix = root[5:].partition("/")
            area = next((a for a, b in BUCKETS.items() if b == bucket), None)
            if area is None:
                raise ValidationError("Bucket không được phép.", hint="Dùng bucket lsth-raw, lsth-work hoặc lsth-out.")
            if prefix:
                prefix = check_key(prefix.rstrip("/")) + "/"
        if area is not None and area not in BUCKETS:
            raise ValidationError("Vùng MinIO không hợp lệ.", hint="Dùng tên vùng như raw hoặc URI s3://lsth-raw/thư-mục/.")
        rows = []
        for selected_area in [area] if area else SEARCH_ORDER:
            store = get_store(selected_area, settings)
            for obj in store.list(prefix=prefix, limit=scan_limit + 1 - len(rows)):
                rows.append({"path": store.uri(obj.key), "name": obj.name,
                             "area": selected_area, "bucket": store.bucket,
                             "suffix": obj.suffix, "size_bytes": obj.size,
                             "readable": obj.suffix.lower() in SUPPORTED,
                             "writable_area": store.writable})
            if len(rows) > scan_limit:
                break
    else:
        selected = resolve_within(local_roots.get(root, root), settings.read_roots,
                                  must_exist=True) if root else None
        if selected is not None and not selected.is_dir():
            raise ValidationError("root phải là thư mục.", hint="Chọn thư mục chứa file cần tìm.")
        rows = list_files(root=selected, settings=settings, limit=scan_limit + 1)

    scan_truncated = len(rows) > scan_limit
    files = []
    for row in rows[:scan_limit]:
        item = dict(row)
        if minio:
            bucket, _, key = item["path"][5:].partition("/")
            if prefix and not key.startswith(prefix):
                continue
            item["root"] = f"s3://{bucket}/" + prefix
            item["relative_path"] = key[len(prefix):]
        else:
            try:
                target = resolve_within(item["path"], settings.read_roots, must_exist=True)
            except PathOutsideRootError:
                continue  # Không đưa symlink ngoài vùng dữ liệu vào kết quả.
            bases = [Path(selected).resolve()] if selected else [p.resolve() for p in settings.read_roots]
            base = next((p for p in bases if target.is_relative_to(p)), None)
            if base is None:
                continue
            item["path"] = str(target)
            item["root"] = str(base)
            item["relative_path"] = target.relative_to(base).as_posix()
        files.append(item)
    return files, scan_truncated, min(len(rows), scan_limit)


def search_files(query: str, root: Optional[str] = None, limit: int = 50,
                 scan_limit: int = 10000, *, settings: Optional[Settings] = None) -> Dict[str, Any]:
    """Tìm các từ trong đường dẫn tương đối, không phân biệt hoa/thường và dấu."""
    _bounded(limit, "limit", 1000)
    _bounded(scan_limit, "scan_limit", 100000)
    needle = query.strip().casefold()
    if not needle:
        raise ValidationError("Từ khoá tìm kiếm rỗng.", hint="Truyền mã hàng, tên file hoặc đuôi file, ví dụ BOM hoặc .pdf.")
    files, scan_truncated, scanned = _inventory(root, settings or get_settings(), scan_limit)
    matches = [f for f in files if _matches_query(f["relative_path"], needle)]
    return {"query": query, "files": matches[:limit], "count": min(len(matches), limit),
            "scanned_count": scanned, "scan_truncated": scan_truncated,
            "truncated": scan_truncated or len(matches) > limit}


def build_tree(root: Optional[str] = None, max_depth: int = 4, limit: int = 200,
               scan_limit: int = 10000, *, query: Optional[str] = None,
               settings: Optional[Settings] = None) -> Dict[str, Any]:
    """Cây file khớp query, giữ thư mục cha; không query thì hiện cây đầy đủ."""
    _bounded(limit, "limit", 1000)
    _bounded(max_depth, "max_depth", 20)
    _bounded(scan_limit, "scan_limit", 100000)
    files, scan_truncated, scanned = _inventory(root, settings or get_settings(), scan_limit)
    query = (query or "").strip()
    if query:
        files = [f for f in files if _matches_query(f["relative_path"], query)]
    roots = {}
    depth_limited = False
    for item in files[:limit]:
        base = item["root"]
        node = roots.setdefault(base, {"name": base, "path": base, "type": "directory", "children": {}})
        parts = item["relative_path"].split("/")
        for index, part in enumerate(parts):
            path = base.rstrip("/") + "/" + "/".join(parts[:index + 1])
            leaf = index == len(parts) - 1
            if leaf:
                node["children"][part] = {"name": part, "path": item["path"],
                                         "type": "file", "size_bytes": item["size_bytes"]}
                break
            node = node["children"].setdefault(part, {
                "name": part, "path": path, "type": "directory", "children": {}})
            if index + 1 >= max_depth:
                node["collapsed"] = True
                depth_limited = True
                break

    def render(node):
        out = dict(node)
        if "children" in out:
            out["children"] = [render(child) for _, child in sorted(out["children"].items())]
        return out

    tree = [render(node) for _, node in sorted(roots.items())]
    lines = []

    def render_text(nodes, indent=""):
        for index, node in enumerate(nodes):
            last = index == len(nodes) - 1
            name = node["name"].replace("\n", "\\n").replace("\r", "\\r")
            if node["type"] == "directory" and not name.endswith("/"):
                name += "/"
            if node.get("collapsed"):
                name += " [thu gọn]"
            lines.append(indent + ("└── " if last else "├── ") + name)
            render_text(node.get("children", []), indent + ("    " if last else "│   "))

    render_text(tree)
    return {"tree": tree, "tree_text": "\n".join(lines), "query": query or None,
            "matched_count": len(files),
            "file_count": min(len(files), limit), "scanned_count": scanned,
            "max_depth": max_depth, "depth_limited": depth_limited,
            "scan_truncated": scan_truncated,
            "truncated": scan_truncated or len(files) > limit,
            "sources": [{"file": f["path"]} for f in files[:limit]]}
