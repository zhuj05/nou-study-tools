import flet as ft

from models import (
    calculate_average_grade,
    calculate_gpa_43,
    calculate_grade,
    format_grade_result,
)


class GradeCalculator(ft.Column):
    def __init__(self):
        self.semester = ft.Dropdown(
            label="功能選擇",
            value="non_summer",
            options=[
                ft.DropdownOption(key="summer", text="暑修"),
                ft.DropdownOption(key="non_summer", text="非暑修"),
                ft.DropdownOption(key="semester_average", text="計算學期總成績平均"),
            ],
            on_select=self.change_semester,
        )
        self.regular = ft.TextField(
            label="平時成績（30%）",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.midterm = ft.TextField(
            label="期中考成績（30%）",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.final = ft.TextField(
            label="期末考成績（40%）",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.average_scores = [
            ft.TextField(
                label=f"科目 {number} 成績（無則免填）",
                keyboard_type=ft.KeyboardType.NUMBER,
                visible=False,
            )
            for number in range(1, 6)
        ]
        self.result = ft.Text("請選擇計算方式並輸入成績後計算。")
        super().__init__(
            controls=[
                ft.Text("空大學期成績計算器（權重版）"),
                self.semester,
                self.regular,
                self.midterm,
                self.final,
                *self.average_scores,
                ft.Button(content="計算學期成績", on_click=self.calculate),
                self.result,
            ]
        )

    def change_semester(self, _):
        mode = self.semester.value
        is_summer = mode == "summer"
        is_average = mode == "semester_average"
        self.regular.visible = not is_average
        self.midterm.visible = not is_summer and not is_average
        self.final.visible = not is_average
        self.final.label = "期末考成績（70%）" if is_summer else "期末考成績（40%）"
        for score in self.average_scores:
            score.visible = is_average
        self.result.value = "請輸入成績後計算。"
        self.page.update()

    def calculate(self, _):
        try:
            if self.semester.value == "semester_average":
                self.calculate_semester_average()
            else:
                self.calculate_course_grade()
        except (TypeError, ValueError):
            self.result.value = "請輸入 0 到 100 之間的有效數字成績。"

        self.page.update()

    def calculate_course_grade(self):
        if self.semester.value == "summer":
            total, letter, gpa, passed = calculate_grade(
                float(self.regular.value),
                float(self.final.value),
            )
        else:
            total, letter, gpa, passed = calculate_grade(
                float(self.regular.value),
                float(self.final.value),
                float(self.midterm.value),
            )
        self.result.value = format_grade_result(
            total, letter, gpa, passed, "學期總成績"
        )

    def calculate_semester_average(self):
        scores = []
        for score_field in self.average_scores:
            value = (score_field.value or "").strip()
            if value:
                scores.append(float(value))
        if not scores:
            self.result.value = "請至少輸入一科成績。"
            return

        total_score, average, letter, gpa, passed = calculate_average_grade(scores)
        letter_43, gpa_43 = calculate_gpa_43(average)
        self.result.value = (
            f"已計算 {len(scores)} 科成績\n"
            f"科目成績加總：{total_score:.1f} 分\n"
            + format_grade_result(average, letter, gpa, passed, "學期成績平均")
            + f"\nGPA（4.3 制）：{letter_43}，積點：{gpa_43:.1f}"
        )
