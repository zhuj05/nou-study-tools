import flet as ft

from views.calculator import GradeCalculator


def main(page: ft.Page):
    page.title = "Semester Grade Calculator(學生自行開發，非官方)"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8F9FA"
    page.add(GradeCalculator())


ft.run(main)
# https://www.long-men.com.tw/newExam/inside?str=EAAE37CA0808C6319E99548B5FC55888
