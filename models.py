"""Pure grade-calculation logic and app data."""

from typing import NamedTuple

# 項目格式: (名稱, 連結, 背景顏色, 文字顏色)
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

# 4.0 制評分標準表 (最低分門檻, 等第, 積點)
GPA_40_SCALE = (
    (80.0, "A", 4.0),
    (70.0, "B", 3.0),
    (60.0, "C", 2.0),
    (50.0, "D", 1.0),
)

# 4.3 制評分標準表 (最低分門檻, 等第, 積點)
GPA_43_SCALE = (
    (90.0, "A+", 4.3),
    (85.0, "A", 4.0),
    (80.0, "A-", 3.7),
    (77.0, "B+", 3.3),
    (73.0, "B", 3.0),
    (70.0, "B-", 2.7),
    (67.0, "C+", 2.3),
    (63.0, "C", 2.0),
    (60.0, "C-", 1.7),
)


class GradeCalculationError(ValueError):
    """自定義成績計算錯誤，便於 UI 攔截與顯示精準訊息。"""
    pass


def _validate_score(score: float, label: str = "成績") -> None:
    """驗證單一成績是否介於 0 到 100 之間。"""
    if not (0.0 <= score <= 100.0):
        raise GradeCalculationError(f"{label}須介於 0 到 100 分之間（目前輸入：{score}）。")


def grade_details(total: float) -> tuple[float, str, float, bool]:
    """計算並回傳單科成績的總分、等第、4.0 制 GPA 以及是否及格。"""
    rounded_total = round(total, 2)

    for threshold, letter, gpa in GPA_40_SCALE:
        if rounded_total >= threshold:
            return rounded_total, letter, gpa, rounded_total >= 60.0

    return rounded_total, "F", 0.0, False


def calculate_grade(
    regular: float, final: float, midterm: float | None = None
) -> tuple[float, str, float, bool]:
    """計算單科加權學期成績。

    - 暑修（midterm 為 None）：平時 30% + 期末 70%
    - 非暑修：平時 30% + 期中 30% + 期末 40%
    """
    _validate_score(regular, "平時成績")
    _validate_score(final, "期末考成績")
    if midterm is not None:
        _validate_score(midterm, "期中考成績")
        total = regular * 0.3 + midterm * 0.3 + final * 0.4
    else:
        total = regular * 0.3 + final * 0.7

    return grade_details(total)


def calculate_average_grade(
    courses: list[tuple[float, float]],
) -> tuple[float, float, str, float, bool]:
    """依多門課程之成績與學分，計算學期加權總平均。

    :param courses: 每門課的 (成績, 學分數) 串列
    :return: (原始成績加總, 學期加權平均, 4.0等第, 4.0積點, 是否及格)
    """
    if not courses:
        raise GradeCalculationError("請至少輸入一門科目的成績與學分。")

    total_credits = 0.0
    weighted_sum = 0.0
    score_sum = 0.0

    for idx, (score, credits) in enumerate(courses, start=1):
        _validate_score(score, f"第 {idx} 科成績")
        if credits <= 0:
            raise GradeCalculationError(f"第 {idx} 科學分數必須大於 0。")

        total_credits += credits
        weighted_sum += score * credits
        score_sum += score

    if total_credits == 0:
        raise GradeCalculationError("學分總和不可為 0。")

    weighted_average = round(weighted_sum / total_credits, 2)
    _, letter, gpa, passed = grade_details(weighted_average)
    return round(score_sum, 1), weighted_average, letter, gpa, passed


def calculate_gpa_43(average: float) -> tuple[str, float]:
    """將學期平均成績轉換為 4.3 制 GPA 等第與積點。"""
    rounded_average = round(average, 2)
    for threshold, letter, gpa in GPA_43_SCALE:
        if rounded_average >= threshold:
            return letter, gpa
    return "F", 0.0


def format_grade_result(
    total: float, letter: str, gpa: float, passed: bool, title: str
) -> str:
    """格式化計算結果為易讀之多行文字訊息。"""
    status = "及格" if passed else "不及格"
    return (
        f"{title}：{total:.1f} 分\n"
        f"狀態：{status}\n"
        f"GPA（4.0 制）：{gpa:.1f}（{letter}）"
    )
