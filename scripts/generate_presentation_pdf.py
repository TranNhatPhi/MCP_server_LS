"""Script tạo tài liệu PDF chuyên nghiệp trình bày cho Ban Giám Đốc Lucky Star (LSTH).
Chủ đề: Hướng dẫn kết nối hệ thống MCP Server cho Claude Cowork, ChatGPT, Antigravity.
"""
from __future__ import annotations

import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Đăng ký font tiếng Việt hệ thống macOS
pdfmetrics.registerFont(TTFont('Arial', '/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', '/System/Library/Fonts/Supplemental/Arial Italic.ttf'))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', '/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf'))

OUTPUT_PATH = "/Users/trannhatphi/Desktop/Lucky star /Huong_Dan_Ket_Noi_MCP_LSTH.pdf"


class NumberedCanvas(canvas.Canvas):
    """Canvas đánh số trang và running header/footer chuyên nghiệp."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages: int):
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (từ trang 2 trở đi)
        if self._pageNumber > 1:
            self.drawString(40, 810, "LUCKY STAR (LSTH) · TÀI LIỆU KẾT NỐI MCP SERVER CHO KHỐI BU")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 804, 555, 804)

        # Footer (mọi trang)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 45, 555, 45)
        
        self.drawString(40, 32, "Bảo mật nội bộ LSTH · Máy soạn nháp, người bấm nút · Chuẩn MCP v1.0")
        page_str = f"Trang {self._pageNumber} / {total_pages}"
        self.drawRightString(555, 32, page_str)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55,
    )

    styles = getSampleStyleSheet()

    # Màu sắc thiết kế
    PRIMARY = colors.HexColor("#1E3A8A")    # Xanh Navy đậm
    SECONDARY = colors.HexColor("#0284C7")  # Xanh lam
    TEXT_DARK = colors.HexColor("#0F172A")  # Xám đen
    MUTED = colors.HexColor("#475569")      # Xám vừa
    BG_LIGHT = colors.HexColor("#F8FAFC")   # Nền nhạt
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Typography
    styles.add(ParagraphStyle(
        'DocHeaderOrg',
        fontName='Arial-Bold',
        fontSize=10,
        leading=14,
        textColor=SECONDARY,
        textTransform='uppercase',
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'DocTitle',
        fontName='Arial-Bold',
        fontSize=20,
        leading=25,
        textColor=PRIMARY,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle',
        fontName='Arial',
        fontSize=11,
        leading=16,
        textColor=MUTED,
        spaceAfter=15,
    ))
    styles.add(ParagraphStyle(
        'MetaBox',
        fontName='Arial',
        fontSize=9,
        leading=14,
        textColor=TEXT_DARK,
    ))
    styles.add(ParagraphStyle(
        'H1',
        fontName='Arial-Bold',
        fontSize=13,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        'H2',
        fontName='Arial-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        'Body',
        fontName='Arial',
        fontSize=9.5,
        leading=14.5,
        textColor=TEXT_DARK,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'BodyBold',
        fontName='Arial-Bold',
        fontSize=9.5,
        leading=14.5,
        textColor=TEXT_DARK,
    ))
    styles.add(ParagraphStyle(
        'CodeSnippet',
        fontName='Arial',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        borderPadding=6,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'TableCell',
        fontName='Arial',
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK,
    ))
    styles.add(ParagraphStyle(
        'TableHead',
        fontName='Arial-Bold',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        'CalloutText',
        fontName='Arial',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#0C4A6E"),
    ))

    story = []

    # -----------------------------------------------------------------------
    # HEADER & METADATA
    # -----------------------------------------------------------------------
    story.append(Paragraph("CÔNG TY CỔ PHẦN MAY LUCKY STAR (LSTH) · KHỐI BU & IT", styles['DocHeaderOrg']))
    story.append(Paragraph("BÁO CÁO KỸ THUẬT: HƯỚNG DẪN KẾT NỐI HỆ THỐNG MCP SERVER", styles['DocTitle']))
    story.append(Paragraph("Tích hợp Trợ lý Trí tuệ Nhân tạo (Claude Cowork, ChatGPT / OpenAI, Antigravity) vào Quy trình Tự động hóa Khối BU", styles['DocSubtitle']))
    
    meta_table_data = [
        [
            Paragraph("<b>Dự án:</b> LSTH Giảm Workload Khối BU (v2.0)", styles['MetaBox']),
            Paragraph("<b>Ngày phát hành:</b> 09/09/2026", styles['MetaBox']),
        ],
        [
            Paragraph("<b>Đối tượng báo cáo:</b> Ban Giám Đốc, Trưởng Khối BU, IT", styles['MetaBox']),
            Paragraph("<b>Giao thức kỹ thuật:</b> MCP (Model Context Protocol)", styles['MetaBox']),
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[260, 255])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # PHẦN 1: TỔNG QUAN GIẢI PHÁP
    # -----------------------------------------------------------------------
    story.append(Paragraph("1. Tổng quan Giải pháp MCP cho Lucky Star", styles['H1']))
    story.append(Paragraph(
        "<b>Model Context Protocol (MCP)</b> là chuẩn kết nối mở do ngành công nghệ phát triển, "
        "cho phép các mô hình Trí tuệ Nhân tạo (AI) kết nối an toàn với kho dữ liệu nội bộ của công ty. "
        "Thay vì phải sao chép dữ liệu khách hàng lên các phần mềm bên ngoài, MCP đóng vai trò là chiếc cầu nối kiểm soát: "
        "AI chỉ được tra cứu thông qua các công cụ đã được cấp phép, có giám sát và truy xuất nguồn gốc.",
        styles['Body']
    ))

    # Hộp Callout 8 nguyên tắc
    callout_data = [[
        Paragraph(
            "<b>CÁC NGUYÊN TẮC BẢO VỆ DOANH NGHIỆP TRONG LSTH-MCP:</b><br/>"
            "• <b>Máy soạn nháp, người bấm nút:</b> AI tuyệt đối không tự ý gửi mail, đặt hàng hay xuất kho; mọi kết quả đều gắn nhãn BẢN NHÁP để Merchandiser phê duyệt.<br/>"
            "• <b>Kho dữ liệu gốc bất khả xâm phạm:</b> Vùng <code>data/raw/</code> chỉ đọc 100%, không ai có thể ghi đè hay làm mất dữ liệu gốc.<br/>"
            "• <b>Một nguồn sự thật & Trả lời kèm nguồn:</b> Mọi thông số (định mức, kích thước) đều chỉ rõ số trang PDF hoặc dòng Excel nguồn.<br/>"
            "• <b>Kiểm toán 100%:</b> Mọi lệnh gọi đều lưu vết lịch sử (Audit log) 12 tháng để hậu kiểm.",
            styles['CalloutText']
        )
    ]]
    callout_table = Table(callout_data, colWidths=[515])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E0F2FE")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BAE6FD")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # PHẦN 2: KIẾN TRÚC KẾT NỐI ĐA NỀN TẢNG
    # -----------------------------------------------------------------------
    story.append(Paragraph("2. Kiến trúc Kết nối Đa Nền tảng (Universal AI Clients)", styles['H1']))
    story.append(Paragraph(
        "Hệ thống máy chủ <b>lsth-mcp</b> được xây dựng độc lập với các nhà cung cấp AI. "
        "Ban Giám Đốc và các phòng ban có thể linh hoạt trang bị bất kỳ công cụ AI nào (Claude, ChatGPT, hoặc Google Antigravity) "
        "mà không bị khóa chặt vào một phần mềm duy nhất:",
        styles['Body']
    ))

    arch_data = [
        [
            Paragraph("<b>Tầng</b>", styles['TableHead']),
            Paragraph("<b>Thành phần</b>", styles['TableHead']),
            Paragraph("<b>Chức năng & Trách nhiệm</b>", styles['TableHead']),
        ],
        [
            Paragraph("<b>1. Giao diện AI</b><br/>(Front-end)", styles['TableCell']),
            Paragraph("• Claude Cowork / Desktop<br/>• ChatGPT / OpenAI Codex<br/>• Antigravity IDE / Desktop", styles['TableCell']),
            Paragraph("Tiếp nhận câu hỏi tự nhiên từ Merchandiser, hiển thị kết quả phân tích bảng biểu, giải thích nguyên phụ liệu.", styles['TableCell']),
        ],
        [
            Paragraph("<b>2. Kênh truyền</b><br/>(Network)", styles['TableCell']),
            Paragraph("• Cloudflare Tunnel (HTTPS)<br/>• Token bảo mật ngẫu nhiên<br/>• Local Stdio Pipe", styles['TableCell']),
            Paragraph("Bảo vệ đường truyền, mã hóa dữ liệu đầu cuối, không mở cổng nguy hiểm ra internet, chống tấn công dò quét.", styles['TableCell']),
        ],
        [
            Paragraph("<b>3. Máy chủ MCP</b><br/>(Core Logic)", styles['TableCell']),
            Paragraph("• 16 MCP Tools chuyên biệt<br/>• SafeWriter & WriteGate<br/>• Bộ bóc tách BOM & Tech Pack", styles['TableCell']),
            Paragraph("Thực thi nghiệp vụ may mặc: bóc tách định mức BOM, đọc bản vẽ kỹ thuật PDF, đối soát sai lệch, xuất file Excel nháp.", styles['TableCell']),
        ],
        [
            Paragraph("<b>4. Kho dữ liệu</b><br/>(Data)", styles['TableCell']),
            Paragraph("• MinIO Object Storage (S3)<br/>• Thư mục data/ nội bộ<br/>• Tài liệu ERP nội bộ", styles['TableCell']),
            Paragraph("Lưu trữ tập trung BOM khách Garan, Haddad, cẩm nang ERP, bảng quy cách đóng gói TLĐG.", styles['TableCell']),
        ],
    ]
    arch_table = Table(arch_data, colWidths=[90, 155, 270])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 14))

    # -----------------------------------------------------------------------
    # PHẦN 3: HƯỚNG DẪN CHI TIẾT TỪNG NỀN TẢNG
    # -----------------------------------------------------------------------
    story.append(Paragraph("3. Hướng dẫn Kết nối Chi tiết cho Từng Nền tảng", styles['H1']))

    # 3.1 Claude Cowork
    story.append(Paragraph("3.1. Claude Cowork / Claude Desktop (Khuyến nghị số 1 cho Merchandiser)", styles['H2']))
    story.append(Paragraph(
        "<b>Đặc điểm:</b> Đây là môi trường lý tưởng nhất cho nhân viên nghiệp vụ (BU/Merchandiser) vì giao diện chat văn phòng "
        "thân thiện, hoàn toàn không có công cụ lập trình hay xem mã nguồn, bảo mật dữ liệu tuyệt đối.",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>Các bước kết nối (chỉ mất 1 phút):</b><br/>"
        "1. Mở ứng dụng <b>Claude Desktop</b> hoặc truy cập <b>Claude Cowork</b> trên trình duyệt.<br/>"
        "2. Vào mục: <b>Customize → Connectors</b> (hoặc biểu tượng Bánh răng Cài đặt).<br/>"
        "3. Bấm vào nút <b>`+`</b> → Chọn <b>Add custom connector</b>.<br/>"
        "4. Dán đường dẫn Cloudflare Tunnel an toàn được cấp vào ô <b>URL</b> (không cần nhập OAuth Client ID):",
        styles['Body']
    ))
    story.append(Paragraph(
        "<code>https://&lt;domain-tunnel&gt;.trycloudflare.com/mcp/&lt;token-bao-mat&gt;</code>",
        styles['CodeSnippet']
    ))
    story.append(Paragraph(
        "5. Bấm <b>Add</b>. Ngay lập tức, 16 công cụ may mặc LSTH sẽ tự động xuất hiện. "
        "Nhân viên có thể gõ ngay: <i>'Bóc tách BOM trong file DEMO_BOM_S2749189.xlsx sheet BOM'</i>.",
        styles['Body']
    ))
    story.append(Spacer(1, 8))

    # 3.2 ChatGPT
    story.append(Paragraph("3.2. ChatGPT / OpenAI Codex / Custom GPTs (Khối Văn phòng & Quản lý)", styles['H2']))
    story.append(Paragraph(
        "<b>Đặc điểm:</b> Dành cho nhân viên hoặc lãnh đạo đã quen sử dụng ChatGPT Plus/Team/Enterprise trên trình duyệt hoặc điện thoại.",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>Các bước thiết lập qua Custom Actions / MCP Adapter:</b><br/>"
        "1. Trên ChatGPT, vào mục <b>Explore GPTs → Create a GPT</b> (Đặt tên: <i>Trợ lý Merchandiser LSTH</i>).<br/>"
        "2. Tại thẻ <b>Configure</b>, cuộn xuống phần <b>Actions</b> và bấm <b>Create new action</b>.<br/>"
        "3. Trong ô <b>Authentication</b>: Chọn <i>API Key</i> hoặc tích hợp qua cổng trung gian Streamable HTTP.<br/>"
        "4. Khai báo Schema dịch vụ từ máy chủ MCP LSTH (Endpoint: <code>/mcp</code>).<br/>"
        "5. Lưu GPT ở chế độ <b>Only people with a link</b> hoặc <b>My Workspace</b> để toàn bộ nhân viên công ty dùng chung.",
        styles['Body']
    ))
    story.append(Spacer(1, 8))

    # 3.3 Antigravity
    story.append(Paragraph("3.3. Google Antigravity (Dành cho Quản lý Kỹ thuật & Power Users)", styles['H2']))
    story.append(Paragraph(
        "<b>Đặc điểm:</b> Dành cho máy tính của quản trị viên hệ thống hoặc chuyên viên IT nội bộ, "
        "hỗ trợ chạy trực tiếp không cần mạng internet (Local Pipe) hoặc qua Cloudflare Tunnel.",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>Cấu hình file <code>.agents/mcp_config.json</code> trong thư mục dự án:</b>",
        styles['Body']
    ))
    config_code = (
        '{\n'
        '  "mcpServers": {\n'
        '    "lsth-mcp-tunnel": {\n'
        '      "serverUrl": "https://&lt;domain-tunnel&gt;.trycloudflare.com/mcp/&lt;token&gt;"\n'
        '    },\n'
        '    "lsth-mcp-local": {\n'
        '      "command": ".../lsth-mcp/.venv/bin/python",\n'
        '      "args": ["-m", "lsth_mcp"]\n'
        '    }\n'
        '  }\n'
        '}'
    )
    story.append(Paragraph(f"<pre>{config_code}</pre>", styles['CodeSnippet']))
    story.append(Paragraph(
        "<b>Cơ chế kiểm soát quyền:</b> Dự án đã trang bị file luật <code>AGENTS.md</code> "
        "ngăn chặn tuyệt đối việc AI đọc trộm mã nguồn; AI chỉ được phép tương tác qua giao thức MCP chuẩn.",
        styles['Body']
    ))
    story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # PHẦN 4: BẢNG SO SÁNH & KHUYẾN NGHỊ
    # -----------------------------------------------------------------------
    story.append(Paragraph("4. Bảng So sánh & Khuyến nghị Lựa chọn cho LSTH", styles['H1']))
    
    comp_data = [
        [
            Paragraph("<b>Tiêu chí</b>", styles['TableHead']),
            Paragraph("<b>Claude Cowork</b>", styles['TableHead']),
            Paragraph("<b>ChatGPT / OpenAI</b>", styles['TableHead']),
            Paragraph("<b>Google Antigravity</b>", styles['TableHead']),
        ],
        [
            Paragraph("<b>Đối tượng phù hợp</b>", styles['TableCell']),
            Paragraph("<b>Merchandiser / BU</b><br/>(Khuyến nghị ưu tiên)", styles['TableCell']),
            Paragraph("Ban Quản lý, Lãnh đạo cần dùng trên di động", styles['TableCell']),
            Paragraph("Bộ phận IT, Quản trị kỹ thuật, Power Users", styles['TableCell']),
        ],
        [
            Paragraph("<b>Độ phức tạp cài đặt</b>", styles['TableCell']),
            Paragraph("Rất dễ (chỉ dán 1 link)", styles['TableCell']),
            Paragraph("Trung bình (cần tạo Action)", styles['TableCell']),
            Paragraph("Trung bình (qua file config)", styles['TableCell']),
        ],
        [
            Paragraph("<b>Trải nghiệm giao diện</b>", styles['TableCell']),
            Paragraph("Giao diện văn phòng, xem bảng tính và tài liệu rất đẹp", styles['TableCell']),
            Paragraph("Giao diện chat đàm thoại linh hoạt", styles['TableCell']),
            Paragraph("Giao diện làm việc kỹ thuật chuyên sâu", styles['TableCell']),
        ],
        [
            Paragraph("<b>Bảo mật dữ liệu</b>", styles['TableCell']),
            Paragraph("Rất cao (Không đọc code máy)", styles['TableCell']),
            Paragraph("Cao (Theo chính sách công ty)", styles['TableCell']),
            Paragraph("Rất cao (Có luật AGENTS.md chặn)", styles['TableCell']),
        ],
        [
            Paragraph("<b>Khả năng chạy ngoại tuyến</b>", styles['TableCell']),
            Paragraph("Cần Cloudflare Tunnel", styles['TableCell']),
            Paragraph("Cần Cloudflare Tunnel", styles['TableCell']),
            Paragraph("Chạy được cả khi mất internet", styles['TableCell']),
        ],
    ]
    comp_table = Table(comp_data, colWidths=[95, 140, 140, 140])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 14))

    # -----------------------------------------------------------------------
    # PHẦN 5: LỘ TRÌNH VÀ BƯỚC TIẾP THEO
    # -----------------------------------------------------------------------
    story.append(Paragraph("5. Đề xuất Kế hoạch Triển khai cho Ban Lãnh Đạo", styles['H1']))
    story.append(Paragraph(
        "Để đưa giải pháp vào ứng dụng thực tế thành công và nâng cao năng suất toàn diện:",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>• Giai đoạn 1 (Thử nghiệm Pilot - Tuần này):</b> Trang bị link kết nối Claude Cowork cho 2-3 bạn Merchandiser "
        "nòng cốt của Team Garan và Team Haddad để thử nghiệm bóc tách BOM và Tech Pack thật trên hệ thống demo.<br/>"
        "<b>• Giai đoạn 2 (Hạ tầng Server cố định - Tháng tới):</b> Chuyển máy chủ MCP từ laptop cá nhân lên một máy chủ nội bộ "
        "(Server phòng IT hoặc Cloud VPS) chạy 24/7 với tên miền cố định của công ty (ví dụ: <code>mcp.luckystar.vn</code>).<br/>"
        "<b>• Giai đoạn 3 (Nhân rộng toàn bộ khối BU):</b> Đào tạo ngắn 30 phút cho toàn bộ Merchandiser cách đặt câu lệnh "
        "đối soát đơn hàng, giúp tiết kiệm trung bình <b>40% - 60% thời gian</b> thao tác thủ công hàng ngày.",
        styles['Body']
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
