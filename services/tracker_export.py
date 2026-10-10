"""學習進度追蹤匯出服務 (純文字與 CSV 資料格式化，無 UI 控制項依賴)。"""

import csv
import io
from typing import Any


def format_exam_line(
    preset_key: str,
    start_d: str,
    end_d: str,
    sh: str,
    sm: str,
    eh: str,
    em: str,
    presets_dict: dict,
) -> str:
    """格式化考試時段字串。"""
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


def _has_meaningful_data(item: dict[str, Any]) -> tuple[bool, str, str]:
    """嚴格判斷科目是否有實質輸入（忽略預設的下拉選單狀態）。"""
    subject = (item.get("subject") or "").strip()
    presets = item.get("time_presets", {})

    m_start = (item.get("midterm_start_date") or "").strip()
    m_end = (item.get("midterm_end_date") or "").strip()
    f_start = (item.get("final_start_date") or "").strip()
    f_end = (item.get("final_end_date") or "").strip()

    midterm_str = format_exam_line(
        item.get("midterm_preset", "period_1"),
        m_start,
        m_end,
        item.get("midterm_start_h", "08"),
        item.get("midterm_start_m", "30"),
        item.get("midterm_end_h", "09"),
        item.get("midterm_end_m", "40"),
        presets,
    ) if (m_start or m_end) else ""

    final_str = format_exam_line(
        item.get("final_preset", "period_1"),
        f_start,
        f_end,
        item.get("final_start_h", "08"),
        item.get("final_start_m", "30"),
        item.get("final_end_h", "09"),
        item.get("final_end_m", "40"),
        presets,
    ) if (f_start or f_end) else ""

    hw1_date = (item.get("hw1_date") or "").strip()
    hw1_status = item.get("hw1", "未完成") or "未完成"
    hw2_date = (item.get("hw2_date") or "").strip()
    hw2_status = item.get("hw2", "未完成") or "未完成"
    memo = (item.get("memo") or "").strip()

    # 嚴格條件：只有科目有字、有選日期、作業狀態不是「未完成」、或有備註時，才算有填
    has_data = bool(
        subject
        or (m_start or m_end)
        or (f_start or f_end)
        or hw1_date
        or (hw1_status != "未完成")
        or hw2_date
        or (hw2_status != "未完成")
        or memo
    )
    return has_data, midterm_str, final_str


def export_tracker_to_line(courses_data: list[dict[str, Any]]) -> str | None:
    """將科目資料清單轉換為適合貼至 LINE 筆記本的多行文字。若無任何資料回傳 None。"""
    lines = [
        "📚 空大學期考試與作業進度紀錄",
        "========================",
    ]

    has_any_data = False
    for idx, item in enumerate(courses_data, start=1):
        has_data, midterm_str, final_str = _has_meaningful_data(item)
        if not has_data:
            continue

        has_any_data = True
        subject = item.get("subject", "").strip()
        display_title = subject if subject else f"科目 {idx}"
        hw1_date = item.get("hw1_date", "").strip()
        hw1_status = item.get("hw1", "未完成")
        hw2_date = item.get("hw2_date", "").strip()
        hw2_status = item.get("hw2", "未完成")
        memo = item.get("memo", "").strip()

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

    if not has_any_data:
        return None

    return "\n".join(lines)


def export_tracker_to_csv(courses_data: list[dict[str, Any]]) -> str | None:
    """將科目資料清單轉換為標準 CSV 格式字串。若無任何資料回傳 None。"""
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

    has_any_data = False
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for item in courses_data:
        has_data, m_str, f_str = _has_meaningful_data(item)
        if not has_data:
            continue

        has_any_data = True
        subject = item.get("subject", "").strip()
        hw1_date = item.get("hw1_date", "").strip()
        hw1_status = item.get("hw1", "未完成")
        hw2_date = item.get("hw2_date", "").strip()
        hw2_status = item.get("hw2", "未完成")
        memo = item.get("memo", "").strip().replace("\n", " ")

        writer.writerow([
            subject,
            m_str,
            f_str,
            hw1_date,
            hw1_status,
            hw2_date,
            hw2_status,
            memo,
        ])

    if not has_any_data:
        return None

    return output.getvalue()