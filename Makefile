.PHONY: help install dev test lint fmt run run-http status eval clean \
        minio-up minio-down minio-logs minio-sync minio-ls

help:
	@echo "install   Cài gói ở chế độ chỉnh sửa được"
	@echo "dev       Cài kèm công cụ phát triển"
	@echo "test      Chạy kiểm thử (không cần thư viện ngoài)"
	@echo "lint      ruff + mypy"
	@echo "run       Chạy MCP server chế độ stdio"
	@echo "run-http  Chạy MCP server chế độ HTTP"
	@echo "status    In bức tranh 17 thành phần"
	@echo "eval      Chạy bộ đánh giá chất lượng F5"
	@echo "minio-up  Bật MinIO (docker) và tạo bucket"
	@echo "minio-sync Đẩy data/ lên MinIO"
	@echo "minio-ls  Xem trong kho object có gì"

install:
	python3 -m pip install -e .

dev:
	python3 -m pip install -e ".[dev,docx]"

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

lint:
	ruff check src tests && mypy

fmt:
	ruff check --fix src tests

run:
	PYTHONPATH=src python3 -m lsth_mcp

run-http:
	PYTHONPATH=src python3 -m lsth_mcp --transport http

status:
	PYTHONPATH=src python3 scripts/status.py

eval:
	PYTHONPATH=src python3 scripts/run_eval.py

minio-up:
	docker compose -f docker/docker-compose.yml up -d
	docker compose -f docker/docker-compose.yml logs minio-init

minio-down:
	docker compose -f docker/docker-compose.yml down

minio-logs:
	docker compose -f docker/docker-compose.yml logs -f minio

minio-sync:
	PYTHONPATH=src python3 scripts/sync_to_minio.py

minio-ls:
	PYTHONPATH=src python3 scripts/sync_to_minio.py --list

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache
