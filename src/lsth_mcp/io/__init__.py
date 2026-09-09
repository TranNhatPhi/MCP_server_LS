"""Lớp đọc/ghi dữ liệu.

Đọc  -> io.readers.*  : trả về ReadResult, luôn kèm nguồn (file/sheet/dòng/trang)
Ghi  -> io.writers.*  : đi qua SafeWriter, có cổng quyền ghi, sao lưu và ghi nguyên tử
"""
from .base import ReadResult, Reader, WriteResult
from .readers.excel import ExcelReader, read_excel
from .readers.jsonio import JsonReader, read_json
from .readers.pdf import PdfDocReader, find_in_pdf, read_pdf
from .readers.tabular import CsvReader, read_csv
from .readers.text import DocxReader, TextReader, read_docx, read_text
from .registry import SUPPORTED, list_files, read_any, reader_for
from .writers.excel import fill_template, write_rows
from .writers.safe import SafeWriter
from .writers.structured import append_jsonl, write_csv, write_json, write_jsonl

__all__ = [
    "ReadResult", "WriteResult", "Reader",
    "read_any", "reader_for", "list_files", "SUPPORTED",
    "read_excel", "read_pdf", "read_csv", "read_json", "read_text", "read_docx",
    "ExcelReader", "PdfDocReader", "CsvReader", "JsonReader", "TextReader", "DocxReader",
    "find_in_pdf",
    "SafeWriter", "write_rows", "fill_template",
    "write_json", "write_jsonl", "append_jsonl", "write_csv",
]
