"""成績試算與及格門檻服務 (業務服務層：組裝領域計算與文字格式化)。"""

import math
from domain.grades import (
    TargetStatus, 
    calculate_average_grade,
    calculate_gpa_43,
    calculate_grade,
    calculate_target_final_score,
    format_grade_result,
)


def _extract_target_result(target_res, default_score: float = 0.0) -> tuple[float, str]:
    """精準提取 TargetResult 物件的分數與狀態。"""
    # 判斷屬性名稱
    if hasattr(target_res, "score"):
        score = target_res.score
    elif hasattr(target_res, "needed_score"):
        score = target_res.needed_score
    elif hasattr(target_res, "needed"):
        score = target_res.needed
    elif isinstance(target_res, (tuple, list)) and len(target_res) >= 2:
        return float(target_res[0]), str(target_res[1])
    else:
        score = default_score

    status = getattr(target_res, "status", "reachable")
    return float(score), str(status)


def evaluate_single_course(
    regular: float,
    final: float | None,
    midterm: float | None = None,
    is_summer: bool = False,
) -> tuple[str, bool]:
    """計算單科成績或試算及格目標。"""
    # ---------------------------------------------------------
    # 情境 1：使用者未輸入期末考成績 -> 試算期末及格門檻
    # ---------------------------------------------------------
    if final is None:
        target_res = calculate_target_final_score(regular, midterm)
        
        
        if is_summer:
            current_acc = regular * 0.3
            calc_default = (60.0 - current_acc) / 0.7
            target_score, status = _extract_target_result(target_res, calc_default)

            if status == "already_passed" or target_score <= 0:
                msg = (
                    f"📊【期末考及格目標試算】\n"
                    f"• 目前平時成績（30%）：{regular:.1f} 分\n"
                    f"• 目前累積得分：{current_acc:.2f} 分\n"
                    f"🎉 目前成績已非常穩健，期末考即使考 0 分也能順利及格！"
                )
                return msg, True
            elif status == "unreachable" or target_score > 100.0:
                msg = (
                    f"📊【期末考及格目標試算】\n"
                    f"• 目前平時成績（30%）：{regular:.1f} 分\n"
                    f"• 期末考需要考取：{target_score:.1f} 分\n"
                    f"⚠️ 期末考即使考滿分 100 分，總分仍無法達到 60 分及格門檻。"
                )
                return msg, False
            else:
                needed_ceil = math.ceil(round(target_score * 10, 6)) / 10
                msg = (
                    f"📊【暑修 期末考及格目標試算】\n"
                    f"• 目前平時成績（30%）：{regular:.1f} 分（已得 {current_acc:.2f} 分）\n"
                    f"• 🎯 期末考（70%）至少需要考：{needed_ceil:.1f} 分 才能達到 60 分及格門檻！\n"
                    f"（期末考滿分 100 分，祝考試順利順暢通關！）"
                )
                return msg, True

        # 非暑修及格試算
        mid = midterm if midterm is not None else 0.0
        accumulated = regular * 0.3 + mid * 0.3
        calc_default = (60.0 - accumulated) / 0.4
        target_score, status = _extract_target_result(target_res, calc_default)

        if status == "already_passed" or target_score <= 0:
            msg = (
                f"📊【期末考及格目標試算】\n"
                f"• 平時成績（30%）：{regular:.1f} 分\n"
                f"• 期中考成績（30%）：{mid:.1f} 分\n"
                f"• 前兩項累積得分：{accumulated:.2f} 分（已達 60 分門檻）\n"
                f"🎉 恭喜！目前累積得分已達標，期末考即使考 0 分也確定順利及格！"
            )
            return msg, True
        elif status == "unreachable" or target_score > 100.0:
            msg = (
                f"📊【期末考及格目標試算】\n"
                f"• 平時成績（30%）：{regular:.1f} 分\n"
                f"• 期中考成績（30%）：{mid:.1f} 分\n"
                f"• 目前累積得分：{accumulated:.2f} 分\n"
                f"• 期末考所需分數：{target_score:.1f} 分\n"
                f"⚠️ 期末考即使考滿分 100 分，總分仍無法達到 60 分及格門檻，請務必掌握作業或面授加分機會。"
            )
            return msg, False
        else:
            needed_ceil = math.ceil(round(target_score * 10, 6)) / 10
            msg = (
                f"📊【非暑修 期末考及格目標試算】\n"
                f"• 平時成績（30%）：{regular:.1f} 分\n"
                f"• 期中考成績（30%）：{mid:.1f} 分\n"
                f"• 目前累積得分：{accumulated:.2f} 分\n"
                f"• 🎯 期末考（40%）至少需要考：{needed_ceil:.1f} 分 才能達到 60 分及格門檻！\n"
                f"（請提早複習備戰，加油！）"
            )
            return msg, True

    # ---------------------------------------------------------
    # 情境 2：期末考有輸入 -> 正常計算總成績
    # ---------------------------------------------------------
    total, letter, gpa, passed = calculate_grade(
        regular, final, midterm if not is_summer else None
    )
    title = "暑修學期總成績" if is_summer else "學期總成績"
    msg = format_grade_result(total, letter, gpa, passed, title)
    return msg, passed


def evaluate_semester_average(
    courses: list[tuple[float, float]],
) -> tuple[str, bool]:
    """計算多門科目加權平均與 4.3 GPA 文字。"""
    total_score, average, letter, gpa, passed = calculate_average_grade(courses)
    letter_43, gpa_43 = calculate_gpa_43(average)

    msg = (
        f"已計算 {len(courses)} 科成績\n"
        f"科目成績加總：{total_score:.1f} 分\n"
        + format_grade_result(average, letter, gpa, passed, "學期成績平均")
        + f"\nGPA（4.3 制）：{letter_43}，積點：{gpa_43:.1f}"
    )
    return msg, passed