"""Pure grade-calculation logic and app data."""


SHORTCUTS = [
    ("空大首頁", "https://www.nou.edu.tw/"),
    ("數位學習平台", "https://uu.nou.edu.tw/mooc/index.php"),
    ("教務行政資訊系統", "https://noustud.nou.edu.tw/"),
    ("空大出版中心", "https://www2.nou.edu.tw/pd/index.aspx"),
    ("空大教務處", "https://studadm.nou.edu.tw/"),
    ("空大視訊面授教室", "https://vc.nou.edu.tw/")
]


def grade_details(total: float) -> tuple[float, str, float, bool]:
    """Return the score, letter grade, GPA, and pass status for a total."""
    if total >= 80:
        letter, gpa = "A", 4.0
    elif total >= 70:
        letter, gpa = "B", 3.0
    elif total >= 60:
        letter, gpa = "C", 2.0
    elif total >= 50:
        letter, gpa = "D", 1.0
    else:
        letter, gpa = "F", 0.0

    return total, letter, gpa, total >= 60
    
    
def calculate_grade(
    regular: float, final: float, midterm: float | None = None
) -> tuple[float, str, float, bool]:
    """Calculate one course's weighted semester grade."""
    scores = (regular, final) if midterm is None else (regular, midterm, final)
    if not all(0 <= score <= 100 for score in scores):
        raise ValueError("請輸入 0 到 100 之間的分數。")

    total = regular * 0.3 + final * 0.7 if midterm is None else (
        regular * 0.3 + midterm * 0.3 + final * 0.4
    )
    return grade_details(total)


def calculate_average_grade(
    scores: list[float],
) -> tuple[float, float, str, float, bool]:
    """Return the total, average, and grade details for completed courses."""
    if not scores:
        raise ValueError("請至少輸入一科成績。")
    if not all(0 <= score <= 100 for score in scores):
        raise ValueError("請輸入 0 到 100 之間的分數。")

    total_score = sum(scores)
    average, letter, gpa, passed = grade_details(total_score / len(scores))
    return total_score, average, letter, gpa, passed


def calculate_gpa_43(average: float) -> tuple[str, float]:
    """Convert a semester average to the requested 4.3-scale GPA."""
    if average >= 90:
        return "A+", 4.3
    if average >= 85:
        return "A", 4.0
    if average >= 80:
        return "A-", 3.7
    if average >= 77:
        return "B+", 3.3
    if average >= 73:
        return "B", 3.0
    if average >= 70:
        return "B-", 2.7
    if average >= 67:
        return "C+", 2.3
    if average >= 63:
        return "C", 2.0
    if average >= 60:
        return "C-", 1.7
    return "F", 0.0


def format_grade_result(
    total: float, letter: str, gpa: float, passed: bool, title: str
) -> str:
    """Format a calculated grade for display."""
    status = "及格" if passed else "不及格"
    return (
        f"{title}：{total:.1f} 分\n"
        f"狀態：{status}\n"
        f"GPA（4.0 制）：{gpa:.1f}（{letter})"

    )
