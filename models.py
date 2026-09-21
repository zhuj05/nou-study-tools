"""Pure grade-calculation logic and app data."""

import datetime
from typing import NamedTuple
import flet as ft

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

# ----------------------------------------------------------------------
# 115 學年度結構化行事曆與大考時程資料
# ----------------------------------------------------------------------
ACADEMIC_CALENDAR_DATA_115: dict[str, dict] = {
    "115_1": {
        "title": "📌 115學年度 第 1 學期（上學期）",
        # 主要大考（用於倒數）：(開始日, 結束日, 考試名稱)
        "major_exams": [
            (datetime.date(2026, 11, 7), datetime.date(2026, 11, 8), "115上期中考試"),
            (datetime.date(2027, 1, 9), datetime.date(2027, 1, 10), "115上期末考試"),
        ],
        "events": [
            (datetime.date(2026, 9, 7), "• 115.09.07 ｜ 開學（課程開播）"),
            (datetime.date(2026, 9, 24), "• 115.09.24 ｜ 115暑學期成績開放網路查詢"),
            (datetime.date(2026, 9, 28), "•🟢 115.09.25 ~115.09.28 ｜ 中秋節及教師節連假 休4天"),
            (datetime.date(2026, 10, 11), "•🟢 115.10.09 ~115.10.11 ｜ 國慶日連假 休3天"),
            (datetime.date(2026, 10, 26), "•🟢 115.10.24 ~115.10.26 ｜ 光復節連假 休3天"),                        
            (datetime.date(2026, 11, 30), "• 115.10.25 ~115.11.30 ｜ 115下招生網路報名"),
            (datetime.date(2026, 11, 8), "• ⭐ 115.11.07 ～ 115.11.08 ｜ 115上期中考試"),
            (datetime.date(2026, 11, 15), "• 115.11.14 ～ 115.11.15 ｜ 115上期中考補考"),
            (datetime.date(2026, 11, 25), "• 115.11.25 ｜ 115上期中考試成績開放網路查詢"),
            (datetime.date(2026, 12, 31), "• 115.12.23 ～ 115.12.31 ｜ 115下線上逾期補選課、補繳費"),
            (datetime.date(2026, 12, 20), "• 115.12.01 ～ 115.12.20 ｜ 115下舊生網路選課繳費"),
            (datetime.date(2026, 12, 27), "•🟢 115.12.25 ~115.12.27 ｜ 行憲紀念日連假 休3天"),            
            
            (datetime.date(2027, 1, 3), "•🟢 116.01.01 ~116.01.03 ｜ 2027元旦 休3天"),
            (datetime.date(2027, 1, 10), "• ⭐ 116.01.09 ～ 116.01.10 ｜ 115上期末考試"),
            (datetime.date(2027, 1, 17), "• 116.01.16 ～ 116.01.17 ｜ 115上期末考補考"),
            (datetime.date(2027, 1, 29), "• 116.01.29 ｜ 115上學期成績開放網路查詢"),
            (datetime.date(2027, 2, 10), "•🟢 116.02.04 ~116.02.10 ｜ 春節假期 休7天"),
            
        ],
    },
    "115_2": {
        "title": "📌 115學年度 第 2 學期（下學期）",
        "major_exams": [
            (datetime.date(2027, 4, 17), datetime.date(2027, 4, 18), "115下期中考試"),
            (datetime.date(2027, 6, 19), datetime.date(2027, 6, 20), "115下期末考試"),
        ],
        "events": [
            (datetime.date(2027, 2, 15), "• 116.02.15 ｜ 115下學期開學（課程開播）"),
            (datetime.date(2027, 3, 1), "•🟢 116.02.27 ~ 03.01 ｜ 和平紀念日 休3天"),
            (datetime.date(2027, 4, 6), "•🟢 116.04.03 ~ 04.06 ｜ 兒童節、清明節 休4天"),
            
            (datetime.date(2027, 4, 18), "• ⭐ 116.04.17 ～ 04.18 ｜ 115下期中考試"),
            (datetime.date(2027, 4, 25), "• 116.04.24 ～ 04.25 ｜ 115下期中考補考"),
            (datetime.date(2027, 5, 2), "•🟢 116.04.30 ~116.05.02 ｜ 勞動節 休3天"),  
            (datetime.date(2027, 5, 20), "• 116.05.01 ～ 05.20 ｜ 116暑期網路選課"),
            (datetime.date(2027, 5, 31), "• 116.05.23 ～ 05.31 ｜ 116暑期線上逾期補選課"),
            (datetime.date(2027, 6, 9), "•🟢 116.06.09 ｜ 端午節 休1天"),
            
            (datetime.date(2027, 6, 20), "• ⭐ 116.06.19 ～ 06.20 ｜ 115下期末考試"),
            (datetime.date(2027, 6, 27), "• 116.06.26 ～ 06.27 ｜ 115下期末考補考"),
        ],
    },
    "115_summer": {
        "title": "📌 115學年度 暑期",
        "major_exams": [],
        "events": [
            (datetime.date(2027, 9, 15), "•🟢 116.09.15 ｜ 中秋節 休1天"),
            (datetime.date(2027, 9, 28), "•🟢 116.09.28 ｜ 教師節 休1天"),
            (datetime.date(2027, 10, 11), "•🟢 116.10.09 ~ 10.11 ｜ 國慶日 休3天"),
            (datetime.date(2027, 10, 25), "•🟢 116.10.23 ~ 10.25 ｜ 光復節 休3天"),
            (datetime.date(2027, 12, 26), "•🟢 116.12.24 ~ 12.26 ｜ 行憲紀念日 休3天"),
            (datetime.date(2028, 1, 2), "•🟢 116.12.31 ~ 117.01.02 ｜ 2028元旦 休3天"),
        ],
    },
}


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


# ----------------------------------------------------------------------
# 重要行事曆檢視元件（考試即時倒數 + 過期自動隱藏 + 水平單選框）
# ----------------------------------------------------------------------
def build_academic_calendar_view(page: ft.Page) -> ft.Container:
    """建構 115 學年度重要行事曆畫面。

    - 頂部自動計算並顯示最近的「期中考 / 期末考倒數天數」（考完隔天自動隱藏）。
    - 根據系統當前日期，自動過濾已結束的事件（只顯示進行中與未來日程）。
    - 上方提供水平單選框切換 115上 / 115下 / 115暑。
    """
    today = datetime.date.today()

    def _get_countdown_badge(semester_key: str) -> ft.Control | None:
        """計算並回傳最近考試的倒數卡片；若考試全數結束則回傳 None。"""
        data = ACADEMIC_CALENDAR_DATA_115.get(semester_key, {})
        major_exams = data.get("major_exams", [])

        for start_date, end_date, exam_name in major_exams:
            if today < start_date:
                days_left = (start_date - today).days
                return ft.Container(
                    bgcolor="#EFF6FF",
                    border=ft.Border.all(1, "#3B82F6"),
                    border_radius=8,
                    padding=10,
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TIMER_OUTLINED, color="#2563EB", size=20),
                            ft.Text(
                                f"距離【{exam_name}】還有 {days_left} 天！",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#1D4ED8",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                )
            elif start_date <= today <= end_date:
                return ft.Container(
                    bgcolor="#FEF2F2",
                    border=ft.Border.all(1, "#EF4444"),
                    border_radius=8,
                    padding=10,
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color="#DC2626", size=20),
                            ft.Text(
                                f"🔥【{exam_name}】今日考試進行中，加油！",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#DC2626",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                )
        return None

    def _get_active_events_controls(semester_key: str) -> list[ft.Control]:
        data = ACADEMIC_CALENDAR_DATA_115.get(semester_key, {})
        title = data.get("title", "")
        events = data.get("events", [])

        rows: list[ft.Control] = []

        # 1. 考試倒數提醒卡片（有即將到來的大考時才插入）
        countdown_card = _get_countdown_badge(semester_key)
        if countdown_card:
            rows.append(countdown_card)

        # 2. 學期標題
        rows.append(
            ft.Text(
                title,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY,
            )
        )

        # 3. 過濾只保留未結束或進行中的事件（今天 <= 結束日期）
        active_events = [text for end_date, text in events if today <= end_date]

        if active_events:
            for text in active_events:
                is_key_exam = "⭐" in text
                rows.append(
                    ft.Text(
                        text,
                        size=14,
                        weight=ft.FontWeight.BOLD if is_key_exam else ft.FontWeight.NORMAL,
                        color="#2563EB" if is_key_exam else None,
                    )
                )
        else:
            rows.append(
                ft.Text(
                    "🎉 本學期重要日程已全數結束或尚未開始公布！",
                    size=14,
                    color=ft.Colors.GREY_500,
                )
            )

        return rows

    # 下方顯示日程文字的容器（預設顯示 115 上）
    calendar_content = ft.Column(
        controls=_get_active_events_controls("115_1"),
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    def on_radio_change(e: ft.ControlEvent) -> None:
        selected_key = e.control.value
        calendar_content.controls = _get_active_events_controls(selected_key)
        page.update()

    # 水平排列的單選框
    semester_radio_group = ft.RadioGroup(
        content=ft.Row(
            controls=[
                ft.Radio(value="115_1", label="115 上"),
                ft.Radio(value="115_2", label="115 下"),
                ft.Radio(value="115_summer", label="115 暑"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        ),
        value="115_1",
        on_change=on_radio_change,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("📅 重要行事曆日程", size=18, weight=ft.FontWeight.BOLD),
                semester_radio_group,
                ft.Divider(height=1, thickness=1),
                calendar_content,
                ft.Divider(height=1, thickness=1),
                ft.Text(
                    "※ 系統已自動過濾過期事件；實際時程請以校方教務處最新公告為準",
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
    )
