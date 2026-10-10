"""重要行事曆日程檢視畫面 (UI 元件層)。"""

import datetime
import flet as ft
from infrastructure.calendar_loader import load_calendar_data

ACADEMIC_CALENDAR_DATA: dict[str, dict] = load_calendar_data()

def build_academic_calendar_view(page: ft.Page) -> ft.Container:
    """建構重要行事曆畫面。"""
    today = datetime.date.today()

    if not ACADEMIC_CALENDAR_DATA:
        return ft.Container(
            content=ft.Text(
                "尚無行事曆資料，請確認 calendar_data.json 是否存在。",
                color=ft.Colors.GREY_500,
            ),
            padding=10,
        )

    available_keys = list(ACADEMIC_CALENDAR_DATA.keys())
    default_sem_key = available_keys[0]

    def _get_countdown_badge(semester_key: str) -> ft.Control | None:
        data = ACADEMIC_CALENDAR_DATA.get(semester_key, {})
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
        data = ACADEMIC_CALENDAR_DATA.get(semester_key, {})
        title = data.get("title", "")
        events = data.get("events", [])
        rows: list[ft.Control] = []

        countdown_card = _get_countdown_badge(semester_key)
        if countdown_card:
            rows.append(countdown_card)

        rows.append(
            ft.Text(
                title,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY,
            )
        )

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

    calendar_content = ft.Column(
        controls=_get_active_events_controls(default_sem_key),
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    def on_radio_change(e: ft.ControlEvent) -> None:
        selected_key = e.control.value
        calendar_content.controls = _get_active_events_controls(selected_key)
        page.update()

    radio_buttons = [
        ft.Radio(value=k, label=v["label"])
        for k, v in ACADEMIC_CALENDAR_DATA.items()
    ]

    semester_radio_group = ft.RadioGroup(
        content=ft.Row(
            controls=radio_buttons,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        ),
        value=default_sem_key,
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