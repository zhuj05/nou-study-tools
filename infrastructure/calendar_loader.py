"""行事曆資料讀取工具 (基礎設施層：隔離外部檔案存取)。"""

import datetime
import json
from pathlib import Path


def load_calendar_data() -> dict[str, dict]:
    """載入專案根目錄下的 calendar_data.json 並解析為 datetime.date 格式。"""
    # 定位專案根目錄 (此檔案位於 infrastructure/ 目錄，上層即為專案根目錄)
    root_dir = Path(__file__).resolve().parent.parent
    json_path = root_dir / "calendar_data.json"

    if not json_path.exists():
        return {}

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logging.getLogger(__name__).warning("無法載入 calendar_data.json: %s", exc)
        return {}

    parsed_data = {}
    for sem_key, sem_val in raw_data.items():
        major_exams = [
            (
                datetime.date.fromisoformat(exam["start"]),
                datetime.date.fromisoformat(exam["end"]),
                exam["name"],
            )
            for exam in sem_val.get("major_exams", [])
            if "start" in exam and "end" in exam and "name" in exam
        ]

        events = [
            (datetime.date.fromisoformat(ev["end_date"]), ev["text"])
            for ev in sem_val.get("events", [])
            if "end_date" in ev and "text" in ev
        ]

        parsed_data[sem_key] = {
            "label": sem_val.get("label", sem_key),
            "title": sem_val.get("title", ""),
            "major_exams": major_exams,
            "events": events,
        }

    return parsed_data