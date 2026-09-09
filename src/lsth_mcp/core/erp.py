"""Bản đồ ERP LSTH — rút từ 9 tài liệu "USE GUIDE ERP VERSION WEB" (2024–2026).

Đây là phần trả lời được cho khoảng trống G1 mà không cần chờ nhà cung cấp: cẩm
nang hướng dẫn người dùng cho biết ERP có những module nào, dữ liệu ra vào bằng
đường nào, và các quy tắc mã hoá nào đang áp dụng.

Ba điểm quan trọng nhất rút ra:

1. ERP là **web app** (erp-app.erpleadingstar.com) và **có app di động** trên cả
   App Store lẫn Google Play. App di động buộc phải nói chuyện với một API HTTP —
   nên câu hỏi G1 đổi từ "có API không" thành "xin được tài liệu và tài khoản cho
   API mà app đang dùng không".
2. **Mọi module đều có nút Export ra Excel** và phần lớn có nút Import. Đường dự
   phòng qua file xuất/nhập mà kiến trúc v1.0 dự trù là chắc chắn dùng được, kể
   cả khi không xin được API.
3. ERP đang phục vụ **12 nhãn khách**, nhiều hơn 6 nhãn trong khảo sát.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

# --------------------------------------------------------------------- hệ thống

#: Ba giao diện web tách biệt, không phải một.
ENDPOINTS = {
    "erp_web": "https://erp-app.erpleadingstar.com/",       # ERP chính
    "portal": "https://erpleadingstar.com/",                # cổng vào
    "internal_purchasing": "https://internalpurchasing.erpleadingstar.com/",
}

#: Bằng chứng mạnh nhất cho việc tồn tại một API HTTP phía sau.
MOBILE_APPS = {
    "ios": "https://apps.apple.com/vn/app/ls-erp/id6756703497",
    "android": "https://play.google.com/store/apps/details?id=com.company.erpmobile",
}

#: Tên đăng nhập là mã số nhân viên, độ dài theo công ty. Dùng để kiểm tra khi
#: nhận bảng nhân sự chuẩn (khoảng trống G9).
EMPLOYEE_CODE_LENGTH: Dict[str, int] = {"LS": 5, "LK": 7, "DA": 6, "TH": 8}

#: CẢNH BÁO BẢO MẬT: cẩm nang ghi mật khẩu mặc định là "123456" và chỉ *khuyến
#: nghị* đổi. Trước khi xin tài khoản riêng cho tự động hoá, cần rà xem còn bao
#: nhiêu tài khoản đang để mật khẩu mặc định.
DEFAULT_PASSWORD_IN_GUIDE = "123456"


# ----------------------------------------------------------------- nhãn khách

#: Mã nhãn hàng trong ERP -> tên. Khảo sát chỉ phủ 6 nhãn có dấu (*).
BRANDS: Dict[str, str] = {
    "DE": "Decathlon",
    "HA": "Haddad",      # *
    "GA": "Garan",       # *
    "IFG": "IFG",
    "LTD": "LTD",        # *
    "H&M": "H&M",        # *
    "JK": "Jako",        # *
    "JO": "JO",
    "OSAKA": "Osaka",    # *
    "GORUCK": "Goruck",
    "KMART": "Kmart",
    "PUMA": "Puma",
}

#: Sáu nhãn đã có dữ liệu khảo sát. Sáu nhãn còn lại là vùng chưa khảo sát.
SURVEYED_BRANDS = ("HA", "GA", "LTD", "H&M", "JK", "OSAKA")


def unsurveyed_brands() -> List[str]:
    """Nhãn khách có trong ERP nhưng chưa có ai khai workload — vùng mù của khảo sát."""
    return [code for code in BRANDS if code not in SURVEYED_BRANDS]


# ------------------------------------------------------- quy tắc mã hoá (F3)

#: Nhãn dùng Contract No (Ref#) làm style number thay vì customer style.
#: Nguồn: "2. USE GUIDE ERP VERSION WEB SO-BOM-PURCHASE", mục Import BOM.
CONTRACT_NO_AS_STYLE = ("HA", "IFG", "JK", "OSAKA")


def style_number_rule(brand: str) -> Tuple[str, str]:
    """Trường nào của Sales Order đóng vai style number khi import BOM.

    Trả về (trường dùng làm style_number, ý nghĩa cột B trong file BOM).

    Quy tắc trích nguyên văn từ cẩm nang:
        "Đối với hàng Haddad, IFG, Jako, Osaka thì style number (1) = Contract NO
        (Ref#) trong sales order, cột B trong file BOM = customer style trong
        sales order. Còn lại thì style number = customer style trong sales order."

    Đây là loại quy tắc ngầm mà F3 sinh ra để giữ — sai chỗ này thì BOM import
    vào nhầm mã hàng.
    """
    code = _normalize_brand(brand)
    if code in CONTRACT_NO_AS_STYLE:
        return ("contract_no", "customer_style")
    return ("customer_style", "customer_style")


def creates_new_ls_style(ls_style_cell: Optional[str]) -> bool:
    """Để trống cột ls style khi Update SO thì ERP tự sinh LS style mới.

    Nguồn: mục Update SO JK. Đây chính là đầu việc tốn 120 phút/lần, 2 lần/tuần
    của chị Trần Sương ("tạo LS style + cập nhật OD của khách").
    """
    return not (ls_style_cell or "").strip()


def valid_vendor_id(code: str) -> bool:
    """ID vendor: "Viết liền không dấu bằng chữ hoa" — nguồn: mục Tạo Vendor."""
    return bool(code) and code.isupper() and code.isascii() and " " not in code


#: Bốn loại code trong màn hình UPC define (nhãn Osaka).
UPC_DEFINE_TYPES = ("ContractNo", "Colorcode", "Gender", "Size")

#: Ba loại đề xuất vải, dùng khi đọc cấu hình Group Mail của ERP.
FABRIC_REQUEST_TYPES = {"FB": "đề xuất vải chính", "FBO": "đề xuất vải bù",
                        "FBS": "đề xuất viền"}

#: Tên sheet file forecast hàng tuần. Nguồn: mục Import FC.
FORECAST_SHEET_PATTERN = "W{week}.{year}"

#: Số đầu thùng vớ: 2 số cuối năm + 2 số tháng + 4–5 số tăng dần. VD 26060001.
CARTON_NUMBER_PATTERN = r"^\d{2}\d{2}\d{4,5}$"


# ------------------------------------------------------------------ trạng thái

class DocStatus(IntEnum):
    """Trạng thái Purchase Request và Purchase Order trong Internal Purchasing."""

    DRAFT = 0
    SUBMIT = 1
    APPROVED = 2
    RELEASE = 3
    RECEIVED = 4

    @property
    def label(self) -> str:
        return {0: "Draft", 1: "Submit", 2: "Approved",
                3: "Release", 4: "Received"}[int(self)]


# -------------------------------------------------------------------- module

@dataclass(frozen=True)
class ErpModule:
    """Một màn hình ERP: đường đi trong menu, và dữ liệu ra vào bằng đường nào."""

    key: str
    path: str                    # đường đi trong menu, đúng như cẩm nang ghi
    can_import: bool = False
    can_export: bool = False
    note: str = ""
    serves: Tuple[str, ...] = ()  # server nào của ta sẽ dùng module này


#: Bản đồ module — chỉ ghi những gì cẩm nang nói rõ, không suy đoán.
MODULES: Dict[str, ErpModule] = {
    m.key: m for m in [
        ErpModule("sales_order", "Sales Order", True, True,
                  "Import theo từng nhãn, mỗi nhãn một template. Riêng H&M có nút "
                  "Read PDF: ERP đã tự bóc PDF sang file update SO.",
                  ("S2", "S5")),
        ErpModule("sales_order_read_pdf", "Sales Order -> Read PDF", True, True,
                  "ĐÃ CÓ SẴN cho H&M. Cần xem kỹ trước khi dựng S1 để không làm trùng.",
                  ("S1", "S2")),
        ErpModule("master_bom", "Master BOM", True, True,
                  "Import -> Save -> Submit (chọn người duyệt theo MSNV) -> Approve/Reject. "
                  "Chỉ sửa item khi chưa submit hoặc đã reject. Có 'Edit via Excel'.",
                  ("S2",)),
        ErpModule("pull_bom", "Sales Order -> Pull BOM type -> Pull BOM", False, False,
                  "Pull từ SO hoặc từ Forecast. Item đã mua thì không xoá được. "
                  "Đây là chỗ có lỗi ERP đã nêu ba lần: báo lỗi lúc Save thay vì lúc Pull.",
                  ("S2",)),
        ErpModule("purchase_order", "Purchase Order", False, True,
                  "Tạo từ Production BOM hoặc từ Purchase Request. Có Report + Export.",
                  ("S2",)),
        ErpModule("purchase_request", "Purchase Request", False, True,
                  "Submit -> duyệt theo tab Log info.", ("S2",)),
        ErpModule("material_packing", "Purchase -> Material Packing", False, True,
                  "Mua phụ liệu đóng gói.", ("S2", "S6")),
        ErpModule("forecast_fcr_master", "System -> FCR Master", True, False,
                  "File Selection đầu mùa, mỗi mùa import một lần.", ("S5",)),
        ErpModule("forecast_report", "Forecast Report", True, True,
                  "File FC hàng tuần, sheet đặt tên W{tuần}.{năm}.", ("S5",)),
        ErpModule("vendor", "System -> Vendor", False, True,
                  "ID vendor viết hoa liền không dấu.", ("S2",)),
        ErpModule("pull_bom_type", "System -> Pull BOM type", False, False,
                  "Danh mục type để pull BOM.", ("S2",)),
        ErpModule("group_mail", "System -> Group Mail", False, False,
                  "Cấu hình To/CC/BCC theo nhãn và loại đề xuất; các mail cách nhau bằng ';'. "
                  "Department: CUTTING_FABRICREQUEST, CUTTING, WAREHOUSE.",
                  ("S4",)),
        ErpModule("upc_define", "System Setup -> System -> UPC define", False, False,
                  "Gán code cho ContractNo, Colorcode, Gender, Size (nhãn Osaka).",
                  ("S3",)),
        ErpModule("shipping_price", "Shipping Price", True, False,
                  "Import đơn giá theo mã hàng (Osaka).", ("M4",)),
        ErpModule("storage_summary", "Inventory -> Organization -> Storage Summary",
                  False, True, "Check tồn kho.", ("S5",)),
        ErpModule("receipt_entry", "Inventory -> Receipt Entry", True, True,
                  "Nhập kho vải/phụ liệu theo PO, tách Lot.", ("S5",)),
        ErpModule("issued_list", "Inventory -> Issued -> Issued List", False, True,
                  "Xuất kho tự do hoặc xuất từ đề xuất vải.", ("S5",)),
        ErpModule("fabric_request", "Production -> Cutting -> FB Request", True, True,
                  "Đề xuất vải; BU approve/reject; ERP tự gửi mail theo Group Mail. "
                  "Đã approve và kho đã xuất thì không reject được.",
                  ("S2", "S4")),
        ErpModule("production_schedule", "Production Schedule", True, True,
                  "Import Sewing Info từ PPC.", ("S5",)),
        ErpModule("final_result", "Final Result", True, True, "Import CFA.", ("S5",)),
        ErpModule("shipping_plan", "Shipping Plan", True, True,
                  "Import shipping info vào TBXH.", ("S5",)),
        ErpModule("kmart_wip", "Kmart WIP", False, True, "Báo cáo WIP.", ("S5",)),
        ErpModule("knitting", "Production -> Knitting", True, True,
                  "Lịch dệt, số đầu thùng vớ (QR), phiếu giao.", ()),
        ErpModule("heat_transfer", "Production -> HeatTransfer", True, True,
                  "Đơn giá ép, sản lượng, lương; báo sản lượng bằng app quét barcode.", ()),
        ErpModule("embroider", "Production -> Embroider", True, True,
                  "Đơn giá thêu, sản lượng, lương.", ()),
    ]
}


def modules_for(server_code: str) -> List[ErpModule]:
    """Các màn hình ERP mà một server của ta sẽ phải chạm tới."""
    return [m for m in MODULES.values() if server_code.upper() in m.serves]


def exportable_modules() -> List[ErpModule]:
    """Module xuất được Excel — đường dự phòng khi chưa xin được API."""
    return [m for m in MODULES.values() if m.can_export]


def _normalize_brand(brand: str) -> str:
    text = (brand or "").strip().upper()
    aliases = {
        "HADDAD": "HA", "GARAN": "GA", "JAKO": "JK", "DECATHLON": "DE",
        "H&M": "H&M", "HM": "H&M", "GORUCK": "GORUCK", "KMART": "KMART",
        "PUMA": "PUMA", "OSAKA": "OSAKA", "LTD": "LTD", "IFG": "IFG",
    }
    return aliases.get(text, text)
