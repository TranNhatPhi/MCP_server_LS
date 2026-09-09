# Triển khai và nối vào Claude Cowork

## Điều kiện bắt buộc phải hiểu trước

**Claude gọi MCP server từ hạ tầng đám mây của Anthropic, không phải từ máy bạn.**
Điều này đúng với mọi client: claude.ai, Claude Desktop, Cowork, app di động.

Hệ quả:

- `localhost` **không dùng được**. Endpoint phải nằm trên internet công khai qua HTTPS.
- Server sau VPN, sau tường lửa công ty, hoặc chỉ có IP nội bộ đều **không kết nối được**.
- Khi lên máy chủ thật, phải mở cho dải IP của Anthropic đi vào.

Giao thức: **Streamable HTTP** (SSE đã bị bỏ). Endpoint nhận POST, mặc định ở `/mcp`.
Mỗi tool phải trả kết quả trong vòng 5 phút.

## Chạy nhanh để thử

```bash
cd lsth-mcp
python3.13 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python scripts/make_demo_data.py    # dữ liệu GIẢ để thử
./scripts/serve.sh                            # dựng server + tunnel công khai
```

Script in ra một URL dạng:

```
https://<ngẫu-nhiên>.trycloudflare.com/mcp/<token>
```

Dừng lại: `./scripts/serve.sh --stop` · Chỉ chạy local: `./scripts/serve.sh --local`

## Nối vào Cowork

1. Mở **Cowork → Customize → Connectors**
2. Nhấn **+** → **Add custom connector**
3. Dán nguyên URL ở trên vào ô URL
4. **Add**

Không cần điền OAuth Client ID/Secret.

### Vì sao token nằm trong đường dẫn chứ không phải header

Giao diện thêm connector chỉ nhận **URL** và (tuỳ chọn) **OAuth Client ID/Secret**.
Nó **không cho nhập header tuỳ ý**, nên không đặt được `Authorization: Bearer`.

Vì vậy server gắn endpoint ở `/mcp/<token>`. Ai không biết token thì router trả
404, không chạm được tới tool nào. Đổi lại: **URL đó chính là mật khẩu** — đừng
dán vào chat chung, đừng đưa vào ảnh chụp màn hình.

Đây là mức đủ cho một buổi thử trên dữ liệu giả. Dùng thật với dữ liệu khách thì
phải chuyển sang OAuth — `MCPServer` nhận `auth_server_provider` và `token_verifier`.

## Thử xem có chạy không, trước khi mở Cowork

```bash
URL=$(cat data/state/public_url.txt)/mcp/$(cat data/state/mcp_token.txt)

curl -s "$(cat data/state/public_url.txt)/health"      # không cần token

curl -s -X POST "$URL" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Thử gì trong Cowork

Server đang ở **chế độ chỉ đọc** và chỉ có **dữ liệu giả**. Vài câu để thử:

| Hỏi Cowork | Kiểm tra điều gì |
|---|---|
| "Liệt kê file trong kho dữ liệu LSTH" | `file_list` |
| "Bóc BOM trong DEMO_BOM_S2749189.xlsx sheet BOM" | `bom_extract` — phải trả 41 dòng **kèm nguồn sheet + số dòng** |
| "Dòng nào trong BOM đó thiếu dữ liệu?" | Phải chỉ ra dòng 42 thiếu `material_code` và `consumption`, **không tự điền** |
| "Bóc tech pack DEMO_TECHPACK_S2749189.pdf" | `techpack_parse` — trả style + mùa, liệt kê trường còn thiếu |
| "Chương trình đang có bao nhiêu thành phần, cái nào bị chặn?" | `program_status` — 17 thành phần, kèm khoảng trống đang chặn |
| "Ghi thử một file vào data/work" | Phải **bị từ chối** với mã `write_not_allowed` |
| "Đọc /etc/passwd" | Phải **bị từ chối** với mã `path_outside_root` |

Hai dòng cuối quan trọng nhất: chúng chứng minh hai lớp chặn đang hoạt động.

Xem lại mọi thứ Cowork đã gọi:

```bash
cat data/audit/calls-$(date +%Y-%m).jsonl | tail -20
```

## Giới hạn của cách chạy này

| Vấn đề | Ảnh hưởng |
|---|---|
| Tunnel `trycloudflare` đổi URL mỗi lần chạy lại | Phải sửa lại connector trong Cowork sau mỗi lần khởi động lại |
| Máy tắt hoặc ngủ là mất kết nối | Chỉ hợp để thử, không hợp để nhiều người dùng |
| Token trong URL, không phải OAuth | Đủ cho dữ liệu giả, không đủ cho dữ liệu khách |
| Đang chạy trên máy cá nhân | Vi phạm nguyên tắc "hai người biết vận hành" nếu để lâu |

## Lên máy chủ thật thì cần gì

Trước khi đưa **dữ liệu khách thật** lên, ba việc phải xong:

1. **Lấp khoảng trống G8** — rà điều khoản bảo mật của 5 khách. Tech pack và BOM
   thuộc vùng Z3 (NDA). Đưa lên một endpoint mà bên thứ ba gọi vào được là đúng
   thứ nhiều hợp đồng gia công cấm. **Đây là việc của BU trưởng, không phải kỹ thuật.**
2. **Chuyển sang OAuth** thay cho token trong URL.
3. **Tên miền cố định + chứng chỉ HTTPS**, và mở tường lửa cho dải IP Anthropic.

Hạ tầng gợi ý: một máy chủ nội bộ có tên miền công khai, hoặc Cloudflare Tunnel
có tên (`cloudflared tunnel create`) thay cho quick tunnel. Docker đã có sẵn trên
máy nếu muốn đóng gói.

## Sự cố hay gặp

| Triệu chứng | Nguyên nhân |
|---|---|
| Cowork báo không kết nối được | Tunnel đã tắt, hoặc URL đã đổi sau khi khởi động lại. Chạy `./scripts/serve.sh` lấy URL mới |
| HTTP 404 | Sai token trong đường dẫn |
| HTTP 421 / "Invalid Host header" | Server chưa biết tên miền công khai. `serve.sh` tự truyền `--public-host`; nếu chạy tay thì phải tự thêm |
| `ModuleNotFoundError: No module named 'lsth_mcp'` | macOS gắn cờ `hidden` lên file `.pth` trong thư mục Desktop khiến Python bỏ qua nó. `serve.sh` tự gỡ cờ bằng `chflags nohidden` và đặt `PYTHONPATH` |
| Tool chạy quá 5 phút | Vượt giới hạn của connector. Chia nhỏ, hoặc thêm tham số `limit` |
