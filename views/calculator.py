import datetime
import math
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import flet as ft


async def set_clipboard_universal(page: ft.Page, text: str) -> bool:
    """全相容跨版本剪貼簿複製常式 (相容 Flet 1.0+、舊版 Flet 與 Pyodide/瀏覽器環境)"""
    if hasattr(page, "clipboard") and page.clipboard is not None:
        try:
            if hasattr(page.clipboard, "set_async"):
                await page.clipboard.set_async(text)
                return True
            elif hasattr(page.clipboard, "set"):
                page.clipboard.set(text)
                return True
        except Exception:
            pass

    if hasattr(page, "set_clipboard_async"):
        try:
            await page.set_clipboard_async(text)
            return True
        except Exception:
            pass
    if hasattr(page, "set_clipboard"):
        try:
            page.set_clipboard(text)
            return True
        except Exception:
            pass

    try:
        import js

        if hasattr(js, "navigator") and hasattr(js.navigator, "clipboard"):
            js.navigator.clipboard.writeText(text)
            return True
        elif (
            hasattr(js, "window")
            and hasattr(js.window, "navigator")
            and hasattr(js.window.navigator, "clipboard")
        ):
            js.window.navigator.clipboard.writeText(text)
            return True
    except Exception:
        pass

    return False


from models import (
    SHORTCUTS,
    build_academic_calendar_view,
    calculate_average_grade,
    calculate_gpa_43,
    calculate_grade,
    format_grade_result,
)


class GradeCalculator(ft.Column):

    def __init__(self):
        self.input_fields = []
        self.credit_selectors = []
        self.input_containers = []
        self.tracker_input_fields = []
        self.font_scale_delta = 0

        # 右上角「功能特色」按鈕
        self.features_btn = ft.TextButton(
            content="功能特色",
            icon=ft.Icons.INFO_OUTLINE,
            icon_color="#3B82F6",
            on_click=self.show_features_dialog,
        )

        self.semester = ft.Dropdown(
            label="功能選擇",
            value="non_summer",
            options=[
                ft.DropdownOption(key="summer", text="暑修"),
                ft.DropdownOption(key="non_summer", text="非暑修"),
                ft.DropdownOption(
                    key="semester_average", text="計算學期總成績平均"
                ),
                ft.DropdownOption(
                    key="exam_hw_tracker", text="考試與作業日期紀錄"
                ),
                ft.DropdownOption(
                    key="academic_calendar", text="重要行事曆日程"
                ),
            ],
            on_select=self.change_semester,
        )
        self.regular = self.create_input("平時成績（30%）")
        self.midterm = self.create_input("期中考成績（30%）")
        self.final = self.create_input(
            "期末考成績（40%）（留空可試算及格目標）"
        )

        # 學期總平均模式欄位 (7 科)
        self.average_scores = []
        self.average_credits = []
        self.average_rows = []
        for number in range(1, 8):
            score = self.create_input(f"科目 {number} 成績（無則免填）")
            credits = self.create_input("學分數")
            self.credit_selectors.append(credits)
            self.average_scores.append(score)
            self.average_credits.append(credits)
            self.average_rows.append(
                ft.Row(
                    controls=[
                        self.input_card(score, expand=2),
                        self.input_card(credits, expand=1),
                    ],
                    visible=False,
                )
            )

        # 7 門科目進度追蹤欄位
        self.tracker_cards_data = []
        tracker_rows_controls = []
        for i in range(1, 8):
            card_data = self._create_tracker_row(f"科目 {i}")
            self.tracker_cards_data.append(card_data)
            tracker_rows_controls.append(card_data["container"])

        # 前 3 科常駐顯示，後 4 科（4~7）預設折疊收合
        self.extra_courses_panel = ft.Column(
            controls=tracker_rows_controls[3:],
            spacing=14,
            visible=False,
        )

        self.toggle_extra_courses_btn = ft.Button(
            content="➕ 展開更多科目 (科目 4～7)",
            bgcolor="#475569",
            color="#FFFFFF",
            height=40,
            on_click=self.toggle_extra_courses,
        )

        # 操作按鈕群
        self.copy_line_btn = ft.Button(
            content="一鍵複製到 LINE 筆記本",
            bgcolor="#06C755",
            color="#FFFFFF",
            height=46,
            expand=True,
            on_click=self.export_to_line,
        )
        self.export_excel_btn = ft.Button(
            content="匯出 / 複製 Excel 紀錄",
            bgcolor="#2563EB",
            color="#FFFFFF",
            height=46,
            expand=True,
            on_click=self.export_to_excel,
        )
        self.clear_form_btn = ft.Button(
            content="清空所有表單",
            bgcolor="#EF4444",
            color="#FFFFFF",
            height=46,
            on_click=self.clear_tracker_form,
        )

        # 頂部使用說明提示區塊
        self.instruction_title = ft.Text(
            "【操作與存檔使用說明】",
            weight=ft.FontWeight.BOLD,
            color="#60A5FA",
            size=15,
        )
        self.instruction_content = ft.Text(
            "• 預設顯示前 3 門常用科目，若修習更多課可點選下方【展開更多科目】。\n"
            "• 每個科目底部皆有【清空此科目】按鈕，可單獨重置不影響其他科目。\n"
            "• 期中/期末考選擇【第 1~6 節】或【線上截止】時自動套用節次，選【自訂時段】可自由微調。\n"
            "• 【推薦】點選下方【一鍵複製到 LINE 筆記本】，點兩下全選複製，直接貼入 LINE 給自己或同學備忘。\n"
            "• 若需轉為試算表，使用電腦，點選【匯出 Excel 紀錄】複製後貼入記事本，另存新檔為「含 BOM 的 UTF-8」CSV 即可用Excel正常開啟不亂碼。",
            size=13,
            color=ft.Colors.WHITE,
        )

        self.instruction_box = ft.Container(
            padding=14,
            border_radius=8,
            border=ft.Border.all(1, "#3B82F6"),
            bgcolor="#1E293B",
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                color="#60A5FA",
                                size=20,
                            ),
                            self.instruction_title,
                        ]
                    ),
                    self.instruction_content,
                ],
            ),
        )

        self.tracker_panel = ft.Column(
            visible=False,
            spacing=14,
            controls=[
                self.instruction_box,
                *tracker_rows_controls[:3],
                self.toggle_extra_courses_btn,
                self.extra_courses_panel,
                ft.Row(
                    controls=[
                        self.copy_line_btn,
                        self.export_excel_btn,
                        self.clear_form_btn,
                    ]
                ),
            ],
        )

        # 重要行事曆檢視容器（預設隱藏）
        self.calendar_panel = ft.Container(visible=False)

        self.result = ft.Text(
            "請選擇計算方式並輸入成績後計算。",
            size=15,
            weight=ft.FontWeight.W_500,
        )
        self.result_box = ft.Container(
            content=self.result,
            padding=14,
            border_radius=10,
            alignment=ft.Alignment(-1, 0),
        )

        self.dark_mode = ft.Switch(
            label="🌙",
            on_change=self.toggle_dark_mode,
        )
        self.font_down_btn = ft.IconButton(
            icon=ft.Icons.TEXT_FIELDS,
            icon_size=18,
            tooltip="字體縮小 (A-)",
            on_click=self.decrease_font_size,
        )
        self.font_up_btn = ft.IconButton(
            icon=ft.Icons.FORMAT_SIZE,
            icon_size=24,
            tooltip="字體放大 (A+)",
            on_click=self.increase_font_size,
        )

        self.settings_row = ft.Row(
            controls=[
                self.dark_mode,
                ft.Row(
                    controls=[
                        ft.Text("字體：", size=13, weight=ft.FontWeight.BOLD),
                        self.font_down_btn,
                        self.font_up_btn,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.action_buttons = ft.Row(
            controls=[
                ft.Button(
                    content="計算學期成績 / 試算及格門檻",
                    bgcolor="#0066CC",
                    color="#FFFFFF",
                    on_click=self.calculate,
                ),
                ft.Button(content="Reset", on_click=self.reset),
            ]
        )

        self.shortcuts_toggle_btn = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_DOWN,
            tooltip="展開常用網頁",
            on_click=self.toggle_shortcuts,
        )

        self.shortcuts_panel = ft.ResponsiveRow(
            spacing=10,
            run_spacing=10,
            controls=[
                ft.Container(
                    col={"xs": 6, "sm": 6, "md": 3, "lg": 3},
                    content=ft.Button(
                        content=name,
                        url=url,
                        expand=True,
                        height=46,
                        bgcolor=bg_color,
                        color=text_color,
                    ),
                )
                for name, url, bg_color, text_color in SHORTCUTS
            ],
            visible=False,
        )

        super().__init__(
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "空大學期成績與課業進度小幫手",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        self.features_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.settings_row,
                self.semester,
                self.input_card(self.regular),
                self.input_card(self.midterm),
                self.input_card(self.final),
                *self.average_rows,
                self.tracker_panel,
                self.calendar_panel,
                self.action_buttons,
                self.result_box,
                ft.Row(
                    controls=[
                        self.shortcuts_toggle_btn,
                        ft.Text("常用網頁", weight=ft.FontWeight.BOLD),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.shortcuts_panel,
                ft.Text(
                    "© 2026 朱家儀. All rights reserved.",
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
                ft.Text(
                    "聯絡作者:\n",
                    size=17,
                    color=ft.Colors.GREY_600,
                    spans=[
                        ft.TextSpan(
                            "nou.tools.dev@gmail.com",
                            url="mailto:",
                            style=ft.TextStyle(
                                color="#3B82F6",
                                decoration=ft.TextDecoration.UNDERLINE,
                            ),
                        )
                    ],
                ),
                ft.Text(
                    "本工具為學生自行開發之非官方輔助工具",
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
            ],
        )
        self.apply_input_theme(False)

    def increase_font_size(self, _):
        if self.font_scale_delta < 6:
            self.font_scale_delta += 2
            self.apply_font_scaling()
            self.show_toast(f"字體已放大 (+{self.font_scale_delta})", "#2563EB")

    def decrease_font_size(self, _):
        if self.font_scale_delta > -2:
            self.font_scale_delta -= 2
            self.apply_font_scaling()
            delta_str = (
                f"+{self.font_scale_delta}"
                if self.font_scale_delta > 0
                else str(self.font_scale_delta)
            )
            self.show_toast(f"字體已縮小 ({delta_str})", "#2563EB")

    def apply_font_scaling(self):
        d = self.font_scale_delta
        for field in self.input_fields:
            field.text_size = 14 + d
        for field in self.tracker_input_fields:
            field.text_size = 13 + d
        self.result.size = 15 + d
        self.instruction_title.size = 15 + d
        self.instruction_content.size = 13 + d
        self.page.update()

    def toggle_extra_courses(self, _):
        is_visible = not self.extra_courses_panel.visible
        self.extra_courses_panel.visible = is_visible
        self.toggle_extra_courses_btn.content = (
            "➖ 收合科目 4～7" if is_visible else "➕ 展開更多科目 (科目 4～7)"
        )
        self.page.update()

    def show_features_dialog(self, _):
        """彈出展示 App 特色、核心功能與使用建議的視窗（已適配手機大字體與連動縮放）。"""
        is_dark = bool(self.dark_mode.value)
        card_bg = "#1E293B" if is_dark else "#F1F5F9"
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK_87
        d = self.font_scale_delta

        def close_dialog(_):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SCHOOL, color="#3B82F6", size=22 + d),
                    ft.Text(
                        "【空大學生自製】功能特色與說明",
                        weight=ft.FontWeight.BOLD,
                        size=16 + d,
                    ),
                ]
            ),
            content=ft.Container(
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    tight=True,
                    spacing=14,
                    controls=[
                        ft.Text(
                            "大家好！這是一款專為空大同學設計的免安裝線上工具，手機點開就能直接用，不用下載任何 App！歡迎同學多加利用 🙌",
                            size=14 + d,
                            color=text_color,
                        ),
                        ft.Container(
                            padding=14,
                            border_radius=8,
                            bgcolor=card_bg,
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Text(
                                        "⭐ 5 大核心功能（點上方功能下拉選單切換）：",
                                        weight=ft.FontWeight.BOLD,
                                        size=15 + d,
                                        color="#3B82F6",
                                    ),
                                    ft.Text(
                                        "• 學期平均計算：最多可算 7 科，右側填入學分數即可加權計算（沒修滿 7 科直接留空）。",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 單科分數計算／門檻試算：支援非暑修與暑修計算；若期末考尚未考（留空），自動計算期末至少需要幾分才能及格！",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 考試／作業日程記錄：支援考試第 1~6 節與線上測驗／報告截止時間快速套用、單科獨立清空，可一鍵匯出至 LINE 筆記本或 Excel 檔！",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 重要行事曆日程：支援 115 上、115 下、115 暑期關鍵時程一鍵切換查詢，重要日子不再漏掉。",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 常用校園連結：整合至畫面下方（可展開），一鍵直達空大首頁、數位學習平台、教務系統、視訊面授教室、出版中心、教務處、學習指導中心及行事曆。",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                ],
                            ),
                        ),
                        # 📲 新增：加入手機桌面 (PWA) 與電腦書籤教學
                        ft.Container(
                            padding=14,
                            border_radius=8,
                            bgcolor=card_bg,
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Text(
                                        "📲 建立捷徑與書籤（免下載安裝，一鍵直達）：",
                                        weight=ft.FontWeight.BOLD,
                                        size=15 + d,
                                        color="#8B5CF6",
                                    ),
                                    ft.Text(
                                        "🤖 Android 用戶（Chrome）：",
                                        weight=ft.FontWeight.BOLD,
                                        size=14 + d,
                                        color="#60A5FA",
                                    ),
                                    ft.Text(
                                        "1. 點擊畫面底部提示的「安裝」按鈕（或點右上角 ⋮ 選單）。\n2. 點選「加到主畫面」或「安裝應用程式」，桌面即會生成像 App 一樣的獨立圖示。",
                                        size=13 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "🍎 iPhone / iPad 用戶（Safari）：",
                                        weight=ft.FontWeight.BOLD,
                                        size=14 + d,
                                        color="#F472B6",
                                    ),
                                    ft.Text(
                                        "1. 務必使用 Safari 開啟，點擊底部工具列中間的「分享」圖示（帶向上箭頭的方框 ⎋）。\n2. 下滑選單點選「加入主畫面」➜ 右上角按「新增」，桌面即可建立全螢幕獨立圖示。",
                                        size=13 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "💻 電腦 PC / Mac 用戶：",
                                        weight=ft.FontWeight.BOLD,
                                        size=14 + d,
                                        color="#10B981",
                                    ),
                                    ft.Text(
                                        "• 鍵盤按下快捷鍵 Ctrl + D（Mac 請按 ⌘ Cmd + D），即可快速將本工具加入瀏覽器書籤列，方便平時隨時開啟！",
                                        size=13 + d,
                                        color=text_color,
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=14,
                            border_radius=8,
                            bgcolor=card_bg,
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text(
                                        "📱 最佳瀏覽建議：",
                                        weight=ft.FontWeight.BOLD,
                                        size=15 + d,
                                        color="#10B981",
                                    ),
                                    ft.Text(
                                        "• 安卓（Android）：建議使用 Chrome 開啟",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 蘋果（iOS）：建議使用 Safari 開啟",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=14,
                            border_radius=8,
                            bgcolor=card_bg,
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text(
                                        "✨ 近期更新亮點：",
                                        weight=ft.FontWeight.BOLD,
                                        size=15 + d,
                                        color="#F59E0B",
                                    ),
                                    ft.Text(
                                        "• 新增期末考及格目標試算（期末考留空即可推算需要考幾分）",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 新增 115 學年度重要行事曆日程查詢（水平按鈕快速切換學期）",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 新增單科獨立清空功能（重填更自由不誤觸）",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 支援字體放大縮小功能（長輩閱讀更輕鬆）",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 畫面瘦身：預設顯示 3 科，手機閱讀不再冗長",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 考試節次智慧切換（第 1~6 節一鍵套用，介面簡潔不雜亂）",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                    ft.Text(
                                        "• 新增🌙模式（夜間讀書不刺眼）",
                                        size=14 + d,
                                        color=text_color,
                                    ),
                                ],
                            ),
                        ),
                        ft.Text(
                            "—\n（非學校官方系統，純同學交流分享，有需要歡迎自行使用！）",
                            size=12 + d,
                            color=ft.Colors.GREY_500,
                        ),
                    ],
                ),
            ),
            actions=[
                ft.Button(content="了解並關閉", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def create_input(self, label: str) -> ft.TextField:
        field = ft.TextField(
            label=label,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
            on_submit=self.calculate,
        )
        self.input_fields.append(field)
        return field

    def input_card(
        self, field: ft.TextField, expand: int | None = None
    ) -> ft.Container:
        card = ft.Container(
            content=field,
            expand=expand,
            shadow=ft.BoxShadow(
                color=ft.Colors.BLACK_12,
                blur_radius=8,
                offset=ft.Offset(0, 2),
            ),
        )
        self.input_containers.append(card)
        return card

    def _create_time_dropdowns(
        self, default_h: str = "08", default_m: str = "30"
    ):
        hours = [f"{i:02d}" for i in range(0, 24)]
        minutes = [f"{i:02d}" for i in range(0, 60, 5)]

        hour_dd = ft.Dropdown(
            label="時",
            value=default_h,
            dense=True,
            width=75,
            options=[ft.DropdownOption(key=h, text=h) for h in hours],
        )
        minute_dd = ft.Dropdown(
            label="分",
            value=default_m,
            dense=True,
            width=75,
            options=[ft.DropdownOption(key=m, text=m) for m in minutes],
        )
        return hour_dd, minute_dd

    def _create_tracker_row(self, placeholder_title: str) -> dict:
        subject_name = ft.TextField(
            label="科目名稱",
            hint_text=placeholder_title,
            dense=True,
            text_size=14,
        )

        def pick_date(target_field: ft.TextField):

            def on_date_picked(e):
                val = e.control.value
                if val:
                    if isinstance(val, str):
                        target_field.value = val.split("T")[0]
                    elif isinstance(val, (datetime.date, datetime.datetime)):
                        adjusted = val + datetime.timedelta(hours=12)
                        target_field.value = (
                            f"{adjusted.year:04d}-{adjusted.month:02d}-{adjusted.day:02d}"
                        )
                    else:
                        target_field.value = str(val)[:10]
                    self.page.update()

            date_picker = ft.DatePicker(on_change=on_date_picked)
            self.page.overlay.append(date_picker)
            self.page.update()
            date_picker.open = True
            self.page.update()

        time_presets = {
            "period_1": (
                "第 1 節",
                "08:30 ~ 09:40",
                "08",
                "30",
                "09",
                "40",
            ),
            "period_2": (
                "第 2 節",
                "10:00 ~ 11:10",
                "10",
                "00",
                "11",
                "10",
            ),
            "period_3": (
                "第 3 節",
                "11:30 ~ 12:40",
                "11",
                "30",
                "12",
                "40",
            ),
            "period_4": (
                "第 4 節",
                "13:30 ~ 14:40",
                "13",
                "30",
                "14",
                "40",
            ),
            "period_5": (
                "第 5 節",
                "15:00 ~ 16:10",
                "15",
                "00",
                "16",
                "10",
            ),
            "period_6": (
                "第 6 節",
                "16:30 ~ 17:40",
                "16",
                "30",
                "17",
                "40",
            ),
            "online_deadline": (
                "線上測驗/報告截止",
                "23:59 截止",
                "00",
                "00",
                "23",
                "59",
            ),
        }

        preset_options = [
            ft.DropdownOption(key="period_1", text="第 1 節 (08:30 ~ 09:40)"),
            ft.DropdownOption(key="period_2", text="第 2 節 (10:00 ~ 11:10)"),
            ft.DropdownOption(key="period_3", text="第 3 節 (11:30 ~ 12:40)"),
            ft.DropdownOption(key="period_4", text="第 4 節 (13:30 ~ 14:40)"),
            ft.DropdownOption(key="period_5", text="第 5 節 (15:00 ~ 16:10)"),
            ft.DropdownOption(key="period_6", text="第 6 節 (16:30 ~ 17:40)"),
            ft.DropdownOption(
                key="online_deadline", text="線上測驗 / 報告截止 (23:59)"
            ),
            ft.DropdownOption(
                key="custom", text="自訂時段 (下方自由微調)"
            ),
        ]

        # 期中考欄位
        midterm_start_date = ft.TextField(
            label="期中考-開始日期",
            dense=True,
            read_only=True,
            expand=True,
            text_size=13,
        )
        midterm_start_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: pick_date(midterm_start_date),
        )
        midterm_start_h, midterm_start_m = self._create_time_dropdowns(
            "08", "30"
        )

        midterm_end_date = ft.TextField(
            label="期中考-結束日期",
            dense=True,
            read_only=True,
            expand=True,
            text_size=13,
        )
        midterm_end_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: pick_date(midterm_end_date),
        )
        midterm_end_h, midterm_end_m = self._create_time_dropdowns("09", "40")

        midterm_time_row1 = ft.Row(
            visible=False,
            controls=[midterm_start_h, ft.Text(":"), midterm_start_m],
        )
        midterm_time_row2 = ft.Row(
            visible=False, controls=[midterm_end_h, ft.Text(":"), midterm_end_m]
        )

        def on_midterm_preset_change(e):
            val = e.control.value
            is_custom = val == "custom"
            midterm_time_row1.visible = is_custom
            midterm_time_row2.visible = is_custom
            if val in time_presets:
                _, _, sh, sm, eh, em = time_presets[val]
                midterm_start_h.value = sh
                midterm_start_m.value = sm
                midterm_end_h.value = eh
                midterm_end_m.value = em
                if midterm_start_date.value and not midterm_end_date.value:
                    midterm_end_date.value = midterm_start_date.value
            self.page.update()

        midterm_preset = ft.Dropdown(
            label="期中快速套用時段",
            value="period_1",
            dense=True,
            options=preset_options,
            on_select=on_midterm_preset_change,
        )

        # 期末考欄位
        final_start_date = ft.TextField(
            label="期末考-開始日期",
            dense=True,
            read_only=True,
            expand=True,
            text_size=13,
        )
        final_start_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: pick_date(final_start_date),
        )
        final_start_h, final_start_m = self._create_time_dropdowns("08", "30")

        final_end_date = ft.TextField(
            label="期末考-結束日期",
            dense=True,
            read_only=True,
            expand=True,
            text_size=13,
        )
        final_end_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: pick_date(final_end_date),
        )
        final_end_h, final_end_m = self._create_time_dropdowns("09", "40")

        final_time_row1 = ft.Row(
            visible=False,
            controls=[final_start_h, ft.Text(":"), final_start_m],
        )
        final_time_row2 = ft.Row(
            visible=False, controls=[final_end_h, ft.Text(":"), final_end_m]
        )

        def on_final_preset_change(e):
            val = e.control.value
            is_custom = val == "custom"
            final_time_row1.visible = is_custom
            final_time_row2.visible = is_custom
            if val in time_presets:
                _, _, sh, sm, eh, em = time_presets[val]
                final_start_h.value = sh
                final_start_m.value = sm
                final_end_h.value = eh
                final_end_m.value = em
                if final_start_date.value and not final_end_date.value:
                    final_end_date.value = final_start_date.value
            self.page.update()

        final_preset = ft.Dropdown(
            label="期末快速套用時段",
            value="period_1",
            dense=True,
            options=preset_options,
            on_select=on_final_preset_change,
        )

        # 作業欄位
        hw1_date = ft.TextField(
            label="作業 1 截止日",
            dense=True,
            read_only=True,
            expand=True,
            text_size=13,
        )
        hw1_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: pick_date(hw1_date),
        )
        hw1_status = ft.Dropdown(
            label="作業 1 狀態",
            value="未完成",
            dense=True,
            options=[
                ft.DropdownOption(key="未完成", text="❌ 未完成"),
                ft.DropdownOption(key="進行中", text="⏳ 進行中"),
                ft.DropdownOption(key="已繳交", text="✅ 已繳交"),
            ],
            expand=True,
        )

        hw2_date = ft.TextField(
            label="作業 2 截止日",
            dense=True,
            read_only=True,
            expand=True,
            text_size=13,
        )
        hw2_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: pick_date(hw2_date),
        )
        hw2_status = ft.Dropdown(
            label="作業 2 狀態",
            value="未完成",
            dense=True,
            options=[
                ft.DropdownOption(key="未完成", text="❌ 未完成"),
                ft.DropdownOption(key="進行中", text="⏳ 進行中"),
                ft.DropdownOption(key="已繳交", text="✅ 已繳交"),
            ],
            expand=True,
        )

        memo_field = ft.TextField(
            label="科目備註（如重點、面授報告細節）",
            dense=True,
            multiline=True,
            min_lines=2,
            max_lines=5,
            text_size=13,
        )

        # 單科獨立清空按鈕
        def clear_single_subject(_):
            subject_name.value = ""
            midterm_preset.value = "period_1"
            midterm_start_date.value = ""
            midterm_start_h.value = "08"
            midterm_start_m.value = "30"
            midterm_end_date.value = ""
            midterm_end_h.value = "09"
            midterm_end_m.value = "40"
            midterm_time_row1.visible = False
            midterm_time_row2.visible = False

            final_preset.value = "period_1"
            final_start_date.value = ""
            final_start_h.value = "08"
            final_start_m.value = "30"
            final_end_date.value = ""
            final_end_h.value = "09"
            final_end_m.value = "40"
            final_time_row1.visible = False
            final_time_row2.visible = False

            hw1_date.value = ""
            hw1_status.value = "未完成"
            hw2_date.value = ""
            hw2_status.value = "未完成"
            memo_field.value = ""
            self.show_toast(
                f"已清空【{placeholder_title}】的所有資料！",
                ft.Colors.ORANGE_700,
            )
            self.page.update()

        clear_single_btn = ft.TextButton(
            icon=ft.Icons.DELETE_OUTLINE,
            content=f"清空上方【{placeholder_title}】資料",
            icon_color="#EF4444",
            style=ft.ButtonStyle(color="#EF4444"),
            on_click=clear_single_subject,
        )

        self.tracker_input_fields.extend([
            subject_name,
            midterm_start_date,
            midterm_end_date,
            final_start_date,
            final_end_date,
            hw1_date,
            hw2_date,
            memo_field,
        ])

        card_container = ft.Container(
            padding=12,
            border_radius=10,
            border=ft.Border.all(1, "#CBD5E1"),
            content=ft.Column(
                spacing=8,
                controls=[
                    subject_name,
                    # 期中考起訖排版
                    ft.Text(
                        "【期中考起訖】",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#60A5FA",
                    ),
                    midterm_preset,
                    ft.Row(
                        controls=[
                            midterm_start_date,
                            midterm_start_btn,
                            midterm_time_row1,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            midterm_end_date,
                            midterm_end_btn,
                            midterm_time_row2,
                        ]
                    ),
                    # 期末考起訖排版
                    ft.Text(
                        "【期末考起訖】",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#60A5FA",
                    ),
                    final_preset,
                    ft.Row(
                        controls=[
                            final_start_date,
                            final_start_btn,
                            final_time_row1,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            final_end_date,
                            final_end_btn,
                            final_time_row2,
                        ]
                    ),
                    # 作業與備註
                    ft.Row(controls=[hw1_date, hw1_btn]),
                    hw1_status,
                    ft.Row(controls=[hw2_date, hw2_btn]),
                    hw2_status,
                    memo_field,
                    # 每個科目下方的獨立清空按鈕
                    ft.Row(
                        controls=[clear_single_btn],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
            ),
        )

        return {
            "container": card_container,
            "subject": subject_name,
            "midterm_preset": midterm_preset,
            "midterm_start_date": midterm_start_date,
            "midterm_start_h": midterm_start_h,
            "midterm_start_m": midterm_start_m,
            "midterm_end_date": midterm_end_date,
            "midterm_end_h": midterm_end_h,
            "midterm_end_m": midterm_end_m,
            "final_preset": final_preset,
            "final_start_date": final_start_date,
            "final_start_h": final_start_h,
            "final_start_m": final_start_m,
            "final_end_date": final_end_date,
            "final_end_h": final_end_h,
            "final_end_m": final_end_m,
            "hw1_date": hw1_date,
            "hw1": hw1_status,
            "hw2_date": hw2_date,
            "hw2": hw2_status,
            "memo": memo_field,
            "time_presets": time_presets,
        }

    def _format_exam_line(
        self,
        preset_key: str,
        start_d: str,
        end_d: str,
        sh: str,
        sm: str,
        eh: str,
        em: str,
        presets_dict: dict,
    ) -> str:
        if not start_d and not end_d:
            return ""

        date_str = start_d or end_d
        if start_d and end_d and start_d != end_d:
            date_range = f"{start_d} 至 {end_d}"
        else:
            date_range = date_str

        if preset_key in presets_dict:
            title, time_info, _, _, _, _ = presets_dict[preset_key]
            if preset_key == "online_deadline":
                return f"{date_range}（{time_info}）"
            return f"{date_range} {title} ({time_info})"

        start_part = f"{start_d} {sh}:{sm}" if start_d else ""
        end_part = f"{end_d} {eh}:{em}" if end_d else ""
        if start_part and end_part:
            return f"{start_part} 至 {end_part}"
        return start_part or end_part

    def show_toast(self, message: str, color: str):
        if self.page:
            self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
            self.page.snack_bar.open = True
            self.page.update()

    def export_to_line(self, _):
        lines = [
            "📚 空大學期考試與作業進度紀錄",
            "========================",
        ]

        has_data = False
        for idx, item in enumerate(self.tracker_cards_data, start=1):
            subject = (item["subject"].value or "").strip()
            presets = item["time_presets"]

            midterm_str = self._format_exam_line(
                item["midterm_preset"].value,
                (item["midterm_start_date"].value or "").strip(),
                (item["midterm_end_date"].value or "").strip(),
                item["midterm_start_h"].value,
                item["midterm_start_m"].value,
                item["midterm_end_h"].value,
                item["midterm_end_m"].value,
                presets,
            )
            final_str = self._format_exam_line(
                item["final_preset"].value,
                (item["final_start_date"].value or "").strip(),
                (item["final_end_date"].value or "").strip(),
                item["final_start_h"].value,
                item["final_start_m"].value,
                item["final_end_h"].value,
                item["final_end_m"].value,
                presets,
            )
            hw1_date = (item["hw1_date"].value or "").strip()
            hw1_status = item["hw1"].value or "未完成"
            hw2_date = (item["hw2_date"].value or "").strip()
            hw2_status = item["hw2"].value or "未完成"
            memo = (item["memo"].value or "").strip()

            if (
                subject
                or midterm_str
                or final_str
                or hw1_date
                or hw2_date
                or memo
            ):
                has_data = True
                display_title = subject if subject else f"科目 {idx}"
                lines.append(f"【{display_title}】")
                if midterm_str:
                    lines.append(f"• 期中考：{midterm_str}")
                if final_str:
                    lines.append(f"• 期末考：{final_str}")
                if hw1_date or hw1_status != "未完成":
                    date_info = f"（截止日：{hw1_date}）" if hw1_date else ""
                    lines.append(f"• 作業 1：{hw1_status} {date_info}")
                if hw2_date or hw2_status != "未完成":
                    date_info = f"（截止日：{hw2_date}）" if hw2_date else ""
                    lines.append(f"• 作業 2：{hw2_status} {date_info}")
                if memo:
                    lines.append(f"• 備註：{memo}")
                lines.append("------------------------")

        if not has_data:
            self.show_toast(
                "請至少填寫一門科目的資料再進行複製！",
                ft.Colors.ORANGE_700,
            )
            return

        line_text = "\n".join(lines)

        export_textfield = ft.TextField(
            value=line_text,
            multiline=True,
            read_only=True,
            min_lines=8,
            max_lines=20,
            text_size=13 + self.font_scale_delta,
            hint_text="請點擊滑鼠左鍵 2 下選取文字複製",
        )

        async def copy_content(_):
            success = await set_clipboard_universal(self.page, line_text)
            if success:
                self.show_toast(
                    "✅ 已成功複製到剪貼簿！可直接至 LINE 按貼上。",
                    ft.Colors.GREEN_700,
                )
            else:
                self.show_toast(
                    "瀏覽器安全性限制，請點擊上方框內全選複製。",
                    ft.Colors.ORANGE_700,
                )

            dialog.open = False
            self.page.update()

        def close_dialog(_):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color="#06C755"),
                    ft.Text("複製到 LINE 筆記本", weight=ft.FontWeight.BOLD),
                ]
            ),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Text(
                        "點選下方【複製到剪貼簿】（或框內點兩下複製），即可貼到 LINE 聊天室或個人記事本：",
                        size=13,
                    ),
                    export_textfield,
                ],
            ),
            actions=[
                ft.Button(
                    content="複製到剪貼簿",
                    bgcolor="#06C755",
                    color="#FFFFFF",
                    on_click=copy_content,
                ),
                ft.Button(content="關閉", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def export_to_excel(self, _):
        headers = [
            "科目名稱",
            "期中考日程",
            "期末考日程",
            "作業1截止日",
            "作業1狀態",
            "作業2截止日",
            "作業2狀態",
            "備註",
        ]
        rows = [headers]

        has_data = False
        for item in self.tracker_cards_data:
            subject = (item["subject"].value or "").strip()
            presets = item["time_presets"]

            m_str = self._format_exam_line(
                item["midterm_preset"].value,
                (item["midterm_start_date"].value or "").strip(),
                (item["midterm_end_date"].value or "").strip(),
                item["midterm_start_h"].value,
                item["midterm_start_m"].value,
                item["midterm_end_h"].value,
                item["midterm_end_m"].value,
                presets,
            )
            f_str = self._format_exam_line(
                item["final_preset"].value,
                (item["final_start_date"].value or "").strip(),
                (item["final_end_date"].value or "").strip(),
                item["final_start_h"].value,
                item["final_start_m"].value,
                item["final_end_h"].value,
                item["final_end_m"].value,
                presets,
            )

            hw1_date = (item["hw1_date"].value or "").strip()
            hw1_status = item["hw1"].value or "未完成"
            hw2_date = (item["hw2_date"].value or "").strip()
            hw2_status = item["hw2"].value or "未完成"
            memo = (item["memo"].value or "").strip().replace("\n", " ")

            if subject or m_str or f_str or hw1_date or hw2_date or memo:
                has_data = True

                def escape_csv(val: str) -> str:
                    if "," in val or '"' in val:
                        return f'"{val.replace('"', '""')}"'
                    return val

                rows.append([
                    escape_csv(subject),
                    escape_csv(m_str),
                    escape_csv(f_str),
                    escape_csv(hw1_date),
                    escape_csv(hw1_status),
                    escape_csv(hw2_date),
                    escape_csv(hw2_status),
                    escape_csv(memo),
                ])

        if not has_data:
            self.show_toast(
                "請至少填寫一門科目的資料再進行匯出！",
                ft.Colors.ORANGE_700,
            )
            return

        csv_text = "\n".join([",".join(row) for row in rows])

        export_textfield = ft.TextField(
            value=csv_text,
            multiline=True,
            read_only=True,
            min_lines=6,
            max_lines=10,
            text_size=13 + self.font_scale_delta,
            hint_text="請點擊滑鼠左鍵 2 下選取文字複製",
        )

        async def copy_content(_):
            success = await set_clipboard_universal(self.page, csv_text)
            if success:
                self.show_toast(
                    "✅ 已成功複製！請貼到記事本，並依說明存為含 BOM 的 UTF-8 CSV。",
                    ft.Colors.GREEN_700,
                )
            else:
                self.show_toast(
                    "瀏覽器安全性限制，請點擊上方框內全選複製。",
                    ft.Colors.ORANGE_700,
                )

            dialog.open = False
            self.page.update()

        def close_dialog(_):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("匯出進度紀錄 (CSV/Excel)", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Text(
                        "【操作步驟】\n"
                        "1. 在下方文字框點滑鼠左鍵 2 下（或按下方按鈕）複製全部內容。\n"
                        "2. 貼入 Windows 記事本，點選「另存新檔」。\n"
                        "3. 存檔類型選「所有檔案 (*.*)」，檔名結尾加上「.csv」。\n"
                        "4. 編碼請選擇「含 BOM 的 UTF-8」，存檔後以 Excel 開啟即可正常顯示中文！",
                        size=12,
                        color=ft.Colors.GREY_300,
                    ),
                    export_textfield,
                ],
            ),
            actions=[
                ft.Button(
                    content="複製全部內容",
                    bgcolor="#2563EB",
                    color="#FFFFFF",
                    on_click=copy_content,
                ),
                ft.Button(content="關閉", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def clear_tracker_form(self, _):
        """清空追蹤表單所有科目。"""
        for item in self.tracker_cards_data:
            item["subject"].value = ""
            item["midterm_preset"].value = "period_1"
            item["midterm_start_date"].value = ""
            item["midterm_start_h"].value = "08"
            item["midterm_start_m"].value = "30"
            item["midterm_end_date"].value = ""
            item["midterm_end_h"].value = "09"
            item["midterm_end_m"].value = "40"
            item["final_preset"].value = "period_1"
            item["final_start_date"].value = ""
            item["final_start_h"].value = "08"
            item["final_start_m"].value = "30"
            item["final_end_date"].value = ""
            item["final_end_h"].value = "09"
            item["final_end_m"].value = "40"
            item["hw1_date"].value = ""
            item["hw1"].value = "未完成"
            item["hw2_date"].value = ""
            item["hw2"].value = "未完成"
            item["memo"].value = ""
        self.show_toast("已清空所有科目的追蹤欄位！", ft.Colors.ORANGE_700)
        self.page.update()

    def apply_input_theme(self, is_dark: bool):
        field_background = "#1E293B" if is_dark else "#FFFFFF"
        border_color = "#334155" if is_dark else "#E5E7EB"
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK_87
        shadow_color = ft.Colors.BLACK_54 if is_dark else ft.Colors.BLACK_12

        field_border = {
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=8,
                side=ft.BorderSide(width=1, color=border_color),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=8,
                side=ft.BorderSide(width=1.5, color="#60A5FA"),
            ),
            ft.ControlState.ERROR: ft.OutlineInputBorder(
                border_radius=8,
                side=ft.BorderSide(width=1.5, color=ft.Colors.RED),
            ),
        }

        all_textfields = self.input_fields + self.tracker_input_fields
        for field in all_textfields:
            field.bgcolor = field_background
            field.focused_bgcolor = field_background
            field.border = field_border
            field.cursor_color = "#60A5FA"
            field.cursor_error_color = ft.Colors.RED
            field.color = text_color
            field.focused_color = text_color
            field.label_style = ft.TextStyle(color=text_color)
            field.error_style = ft.TextStyle(color=ft.Colors.RED)

        for card in self.input_containers:
            card.shadow = ft.BoxShadow(
                color=shadow_color,
                blur_radius=8,
                offset=ft.Offset(0, 2),
            ),

        for item in self.tracker_cards_data:
            item["container"].border = ft.Border.all(
                1, "#334155" if is_dark else "#E2E8F0"
            )
            item["container"].bgcolor = "#1E293B" if is_dark else "#FFFFFF"

        if hasattr(self, "instruction_box"):
            self.instruction_box.bgcolor = "#1E293B" if is_dark else "#EFF6FF"
            self.instruction_box.border = ft.Border.all(
                1, "#3B82F6" if is_dark else "#93C5FD"
            )
            self.instruction_content.color = (
                ft.Colors.WHITE if is_dark else ft.Colors.BLACK_87
            )

    def change_semester(self, _):
        mode = self.semester.value
        is_summer = mode == "summer"
        is_average = mode == "semester_average"
        is_tracker = mode == "exam_hw_tracker"
        is_calendar = mode == "academic_calendar"

        is_grade_calc = not is_tracker and not is_average and not is_calendar
        self.regular.visible = is_grade_calc
        self.midterm.visible = is_grade_calc and not is_summer
        self.final.visible = is_grade_calc
        self.final.label = (
            "期末考成績（70%）（留空可試算及格目標）"
            if is_summer
            else "期末考成績（40%）（留空可試算及格目標）"
        )

        for row in self.average_rows:
            row.visible = is_average

        self.tracker_panel.visible = is_tracker

        # 當切換到行事曆時動態載入元件
        if is_calendar:
            self.calendar_panel.content = build_academic_calendar_view(
                self.page
            )
            self.calendar_panel.visible = True
        else:
            self.calendar_panel.visible = False

        # 行事曆或作業紀錄模式下隱藏算分按鈕與成績卡片
        self.action_buttons.visible = not is_tracker and not is_calendar
        self.result_box.visible = not is_tracker and not is_calendar

        self.clear_all_errors()
        if not is_tracker and not is_calendar:
            self.show_result("請輸入成績後計算。")
        self.page.update()

    def toggle_dark_mode(self, _):
        is_dark = self.dark_mode.value
        self.page.theme_mode = (
            ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        )
        self.page.bgcolor = "#0F172A" if is_dark else "#F8F9FA"
        self.apply_input_theme(is_dark)

        if self.result_box.border is not None:
            self.result.color = (
                ft.Colors.WHITE if is_dark else ft.Colors.BLACK_87
            )
        self.page.update()

    def show_result(self, message: str, passed: bool | None = None):
        self.result.value = message
        is_dark = bool(self.dark_mode.value)

        if passed is None:
            self.result_box.bgcolor = "#1E293B" if is_dark else "#F1F5F9"
            self.result_box.border = ft.Border.all(
                1, "#334155" if is_dark else "#CBD5E1"
            )
            self.result.color = (
                ft.Colors.WHITE if is_dark else ft.Colors.BLACK_87
            )
        else:
            self.result_box.border = None
            if passed:
                self.result_box.bgcolor = "#064E3B" if is_dark else "#DCFCE7"
                self.result.color = "#A7F3D0" if is_dark else "#14532D"
            else:
                self.result_box.bgcolor = "#7F1D1D" if is_dark else "#FEE2E2"
                self.result.color = "#FECACA" if is_dark else "#7F1D1D"

    def toggle_shortcuts(self, _):
        is_visible = not self.shortcuts_panel.visible
        self.shortcuts_panel.visible = is_visible
        self.shortcuts_toggle_btn.icon = (
            ft.Icons.KEYBOARD_ARROW_UP
            if is_visible
            else ft.Icons.KEYBOARD_ARROW_DOWN
        )
        self.shortcuts_toggle_btn.tooltip = (
            "收合常用網頁" if is_visible else "展開常用網頁"
        )
        self.page.update()

    def clear_all_errors(self):
        for field in self.input_fields:
            field.error_text = None

    def reset(self, _):
        self.semester.value = "non_summer"
        self.regular.value = ""
        self.midterm.value = ""
        self.final.value = ""
        for score, credits in zip(self.average_scores, self.average_credits):
            score.value = ""
            credits.value = ""
        self.clear_all_errors()
        self.change_semester(None)

    def calculate(self, _):
        self.clear_all_errors()
        try:
            if self.semester.value == "semester_average":
                self.calculate_semester_average()
            else:
                self.calculate_course_grade()
        except (TypeError, ValueError) as err:
            self.show_result(f"請檢查輸入：{err}")
        self.page.update()

    def calculate_course_grade(self):
        regular_val = (self.regular.value or "").strip()
        final_val = (self.final.value or "").strip()
        midterm_val = (self.midterm.value or "").strip()

        if not regular_val:
            self.regular.error_text = "請輸入平時成績"
            raise ValueError("請輸入平時成績。")

        try:
            reg_score = float(regular_val)
        except ValueError:
            self.regular.error_text = "請輸入有效數字"
            raise ValueError("平時成績請輸入有效數字。")

        if not (0.0 <= reg_score <= 100.0):
            self.regular.error_text = "需介於 0 到 100 分"
            raise ValueError("平時成績須介於 0 到 100 分之間。")

        # -------------------------------------------------------------
        # 情境 A：暑修模式 (平時 30% + 期末 70%)
        # -------------------------------------------------------------
        if self.semester.value == "summer":
            # 使用者未輸入期末考成績 -> 試算及格門檻
            if not final_val:
                needed = (60.0 - reg_score * 0.3) / 0.7
                if needed <= 0:
                    msg = (
                        f"📊【期末考及格目標試算】\n"
                        f"• 目前平時成績（30%）：{reg_score:.1f} 分\n"
                        f"• 目前累積得分：{reg_score * 0.3:.2f} 分\n"
                        f"🎉 目前成績已非常穩健，期末考即使考 0 分也能順利及格！"
                    )
                    self.show_result(msg, True)
                elif needed > 100.0:
                    needed_rounded = round(needed, 1)
                    msg = (
                        f"📊【期末考及格目標試算】\n"
                        f"• 目前平時成績（30%）：{reg_score:.1f} 分\n"
                        f"• 期末考需要考取：{needed_rounded:.1f} 分\n"
                        f"⚠️ 期末考即使考滿分 100 分，總分仍無法達到 60 分及格門檻。"
                    )
                    self.show_result(msg, False)
                else:
                    needed_ceil = math.ceil(needed * 10) / 10
                    current_acc = reg_score * 0.3
                    msg = (
                        f"📊【暑修 期末考及格目標試算】\n"
                        f"• 目前平時成績（30%）：{reg_score:.1f} 分（已得 {current_acc:.2f} 分）\n"
                        f"• 🎯 期末考（70%）至少需要考：{needed_ceil:.1f} 分 才能達到 60 分及格門檻！\n"
                        f"（期末考滿分 100 分，祝考試順利順暢通關！）"
                    )
                    self.show_result(msg, True)
                return

            # 有填寫期末考成績 -> 正常計算學期成績
            try:
                fin_score = float(final_val)
            except ValueError:
                self.final.error_text = "請輸入有效數字"
                raise ValueError("期末考成績請輸入有效數字。")

            total, letter, gpa, passed = calculate_grade(reg_score, fin_score)
            self.show_result(
                format_grade_result(
                    total, letter, gpa, passed, "暑修學期總成績"
                ),
                passed,
            )
            return

        # -------------------------------------------------------------
        # 情境 B：非暑修模式 (平時 30% + 期中 30% + 期末 40%)
        # -------------------------------------------------------------
        if not midterm_val:
            self.midterm.error_text = "請輸入期中考成績"
            raise ValueError("請輸入期中考成績。")

        try:
            mid_score = float(midterm_val)
        except ValueError:
            self.midterm.error_text = "請輸入有效數字"
            raise ValueError("期中考成績請輸入有效數字。")

        if not (0.0 <= mid_score <= 100.0):
            self.midterm.error_text = "需介於 0 到 100 分"
            raise ValueError("期中考成績須介於 0 到 100 分之間。")

        # 使用者只有輸入平時成績和期中考成績（期末考未填）-> 試算期末考需要幾分及格
        if not final_val:
            accumulated = reg_score * 0.3 + mid_score * 0.3
            needed = (60.0 - accumulated) / 0.4
            if needed <= 0:
                msg = (
                    f"📊【期末考及格目標試算】\n"
                    f"• 平時成績（30%）：{reg_score:.1f} 分\n"
                    f"• 期中考成績（30%）：{mid_score:.1f} 分\n"
                    f"• 前兩項累積得分：{accumulated:.2f} 分（已達 60 分門檻）\n"
                    f"🎉 恭喜！目前累積得分已達標，期末考即使考 0 分也確定順利及格！"
                )
                self.show_result(msg, True)
            elif needed > 100.0:
                needed_rounded = round(needed, 1)
                msg = (
                    f"📊【期末考及格目標試算】\n"
                    f"• 平時成績（30%）：{reg_score:.1f} 分\n"
                    f"• 期中考成績（30%）：{mid_score:.1f} 分\n"
                    f"• 目前累積得分：{accumulated:.2f} 分\n"
                    f"• 期末考所需分數：{needed_rounded:.1f} 分\n"
                    f"⚠️ 期末考即使考滿分 100 分，總分仍無法達到 60 分及格門檻，請務必掌握作業或面授加分機會。"
                )
                self.show_result(msg, False)
            else:
                needed_ceil = math.ceil(needed * 10) / 10
                msg = (
                    f"📊【非暑修 期末考及格目標試算】\n"
                    f"• 平時成績（30%）：{reg_score:.1f} 分\n"
                    f"• 期中考成績（30%）：{mid_score:.1f} 分\n"
                    f"• 目前累積得分：{accumulated:.2f} 分\n"
                    f"• 🎯 期末考（40%）至少需要考：{needed_ceil:.1f} 分 才能達到 60 分及格門檻！\n"
                    f"（請提早複習備戰，加油！）"
                )
                self.show_result(msg, True)
            return

        # 若使用者三個欄位皆填寫 -> 正常計算學期總成績
        try:
            fin_score = float(final_val)
        except ValueError:
            self.final.error_text = "請輸入有效數字"
            raise ValueError("期末考成績請輸入有效數字。")

        total, letter, gpa, passed = calculate_grade(
            reg_score, fin_score, mid_score
        )
        self.show_result(
            format_grade_result(total, letter, gpa, passed, "學期總成績"),
            passed,
        )

    def calculate_semester_average(self):
        courses = []
        has_error = False

        for score_field, credit_field in zip(
            self.average_scores, self.average_credits
        ):
            score_str = (score_field.value or "").strip()
            credit_str = (credit_field.value or "").strip()

            if not score_str and not credit_str:
                continue

            if not score_str:
                score_field.error_text = "請填寫成績"
                has_error = True
            if not credit_str:
                credit_field.error_text = "請填寫學分"
                has_error = True

            if score_str and credit_str:
                courses.append((float(score_str), float(credit_str)))

        if has_error:
            raise ValueError("每科請同時輸入成績與學分。")

        if not courses:
            self.show_result("請至少輸入一科成績與學分。")
            return

        total_score, average, letter, gpa, passed = calculate_average_grade(
            courses
        )
        letter_43, gpa_43 = calculate_gpa_43(average)
        self.show_result(
            f"已計算 {len(courses)} 科成績\n"
            f"科目成績加總：{total_score:.1f} 分\n"
            + format_grade_result(
                average, letter, gpa, passed, "學期成績平均"
            )
            + f"\nGPA（4.3 制）：{letter_43}，積點：{gpa_43:.1f}",
            passed,
        )
