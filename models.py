"""應用程式資料常量與向前相容模組匯出。"""

# 常用連結捷徑設定 (項目格式: 名稱, 連結, 背景顏色, 文字顏色)
SHORTCUTS: list[tuple[str, str, str, str]] = [
    ("空大首頁", "https://www.nou.edu.tw/", "#E6FFFA", "#006D5B"),
    ("數位學習平台", "https://uu.nou.edu.tw/mooc/index.php", "#EBF8FF", "#2B6CB0"),
    ("教務行政資訊系統", "https://noustud.nou.edu.tw/", "#EDF2F7", "#4A5568"),
    ("空大出版中心", "https://www2.nou.edu.tw/pd/index.aspx", "#FEFCBF", "#744210"),
    ("空大教務處", "https://studadm.nou.edu.tw/", "#FFF5F5", "#9B2C2C"),
    ("視訊面授教室", "https://vc.nou.edu.tw/", "#FFEDD5", "#C2410C"),
    ("學習指導中心", "https://www.nou.edu.tw/Home/Center", "#F3E8FF", "#6B21A8"),
    ("行事曆", "https://studadm.nou.edu.tw/FileManage/select_files#cal", "#E2E8F0", "#334155"),
]

# ----------------------------------------------------------------------
# 向下相容轉發：從領域層 (domain) 匯出計算邏輯
# ----------------------------------------------------------------------
from domain.grades import (
    GPA_40_SCALE,
    GPA_43_SCALE,
    GradeCalculationError,
    calculate_average_grade,
    calculate_gpa_43,
    calculate_grade,
    calculate_target_final_score,
    format_grade_result,
    grade_details,
)

# ----------------------------------------------------------------------
# 向下相容轉發：從基礎設施與檢視層匯出
# ----------------------------------------------------------------------
from infrastructure.calendar_loader import load_calendar_data
from views.calendar_view import build_academic_calendar_view

__all__ = [
    "SHORTCUTS",
    "GPA_40_SCALE",
    "GPA_43_SCALE",
    "GradeCalculationError",
    "calculate_grade",
    "calculate_target_final_score",
    "calculate_average_grade",
    "calculate_gpa_43",
    "format_grade_result",
    "grade_details",
    "load_calendar_data",
    "build_academic_calendar_view",
]