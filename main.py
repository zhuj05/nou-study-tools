import flet as ft

from views.calculator import GradeCalculator


def main(page: ft.Page):
    page.title = "空大學業小幫手｜成績試算・課業日程・直連校方官網（非官方）"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8F9FA"
    page.add(GradeCalculator())


ft.run(main)
# https://www.long-men.com.tw/newExam/inside?str=EAAE37CA0808C6319E99548B5FC55888
