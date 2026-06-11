"""
╔══════════════════════════════════════════════╗
║      STUDENT RECORD MANAGEMENT SYSTEM        ║
╚══════════════════════════════════════════════╝

Features  : Add / View / Search / Edit / Delete / Export students
Storage   : CSV file  (students.csv — auto-created on first run)
Concepts  : dict, list, CSV file I/O, CRUD, modular functions,
            exception handling, input validation
"""

import csv
import os
import time

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_FILE   = "students.csv"
CSV_HEADERS = ["id", "name", "age", "subjects", "marks"]   # marks = avg float

# ── Colour helpers (optional, degrades gracefully on plain terminals) ──────────
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✔  {msg}{RESET}")
def err(msg):   print(f"  {RED}✘  {msg}{RESET}")
def info(msg):  print(f"  {CYAN}ℹ  {msg}{RESET}")
def warn(msg):  print(f"  {YELLOW}⚠  {msg}{RESET}")

# ══════════════════════════════════════════════════════════════════════════════
#  FILE HANDLING  — read / write CSV
# ══════════════════════════════════════════════════════════════════════════════

def load_students() -> list[dict]:
    """Read all records from CSV; return list of dicts."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            students = []
            for row in reader:
                # Restore correct types after CSV round-trip
                row["id"]    = int(row["id"])
                row["age"]   = int(row["age"])
                row["marks"] = float(row["marks"])
                students.append(row)
            return students
    except (IOError, ValueError) as e:
        err(f"Could not read {DATA_FILE}: {e}")
        return []


def save_students(students: list[dict]) -> None:
    """Write all records to CSV."""
    try:
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(students)
    except IOError as e:
        err(f"Could not save data: {e}")


def next_id(students: list[dict]) -> int:
    """Auto-increment ID (1-based)."""
    return max((s["id"] for s in students), default=0) + 1


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def prompt(label: str, default: str = "") -> str:
    """Single-line prompt; returns default if empty input."""
    hint = f" [{default}]" if default else ""
    try:
        val = input(f"  {label}{hint}: ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit("\n  Exiting. Goodbye!")


def get_int(label: str, lo: int, hi: int, default: int | None = None) -> int:
    """Prompt for an integer in range [lo, hi]."""
    while True:
        raw = prompt(label, str(default) if default is not None else "")
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            warn(f"Please enter a number between {lo} and {hi}.")
        except ValueError:
            warn("That's not a valid number.")


def get_float(label: str, lo: float, hi: float, default: float | None = None) -> float:
    """Prompt for a float in range [lo, hi]."""
    while True:
        raw = prompt(label, str(default) if default is not None else "")
        try:
            val = float(raw)
            if lo <= val <= hi:
                return val
            warn(f"Please enter a value between {lo} and {hi}.")
        except ValueError:
            warn("That's not a valid number.")


def grade(marks: float) -> str:
    """Return letter grade from average marks (0–100)."""
    if marks >= 90: return "A+"
    if marks >= 80: return "A"
    if marks >= 70: return "B"
    if marks >= 60: return "C"
    if marks >= 50: return "D"
    return "F"


# ══════════════════════════════════════════════════════════════════════════════
#  DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def print_banner():
    print(f"\n{BOLD}{'═'*50}")
    print("   📚  STUDENT RECORD MANAGEMENT SYSTEM")
    print(f"{'═'*50}{RESET}")


def print_menu():
    print(f"""
{BOLD}  ┌─────────────────────────────┐
  │         MAIN MENU           │
  ├─────────────────────────────┤
  │  1 │ Add Student            │
  │  2 │ View All Students      │
  │  3 │ Search Student         │
  │  4 │ Edit Student           │
  │  5 │ Delete Student         │
  │  6 │ View Summary / Stats   │
  │  0 │ Exit                   │
  └─────────────────────────────┘{RESET}""")


def print_table(students: list[dict], title: str = "Student Records") -> None:
    """Render a formatted table for a list of students."""
    if not students:
        warn("No records to display.")
        return

    print(f"\n  {BOLD}{title}{RESET}")
    print(f"  {'─'*72}")
    print(f"  {'ID':>4}  {'Name':<20}  {'Age':>3}  {'Subjects':<20}  {'Avg Marks':>9}  {'Grade':>5}")
    print(f"  {'─'*72}")
    for s in students:
        g = grade(s["marks"])
        colour = GREEN if g in ("A+","A","B") else (YELLOW if g in ("C","D") else RED)
        print(
            f"  {s['id']:>4}  {s['name']:<20}  {s['age']:>3}  "
            f"{s['subjects']:<20}  {s['marks']:>9.1f}  "
            f"{colour}{g:>5}{RESET}"
        )
    print(f"  {'─'*72}")
    print(f"  Total: {len(students)} record(s)\n")


# ══════════════════════════════════════════════════════════════════════════════
#  CRUD OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. ADD ─────────────────────────────────────────────────────────────────────
def add_student(students: list[dict]) -> None:
    print(f"\n{BOLD}  ── Add New Student ──{RESET}")

    name = ""
    while not name:
        name = prompt("Name").title()
        if not name:
            warn("Name cannot be empty.")

    age     = get_int("Age", 5, 100)
    subjects_raw = prompt("Subjects (comma-separated, e.g. Math, Science)")
    subjects = ", ".join(s.strip().title() for s in subjects_raw.split(",") if s.strip()) or "N/A"
    marks   = get_float("Average Marks (0–100)", 0, 100)

    student = {
        "id":       next_id(students),
        "name":     name,
        "age":      age,
        "subjects": subjects,
        "marks":    round(marks, 1),
    }
    students.append(student)
    save_students(students)
    ok(f"Student '{name}' added with ID {student['id']}. Grade: {grade(marks)}")


# ── 2. VIEW ALL ────────────────────────────────────────────────────────────────
def view_all(students: list[dict]) -> None:
    print_table(students, "All Student Records")


# ── 3. SEARCH ──────────────────────────────────────────────────────────────────
def search_student(students: list[dict]) -> None:
    print(f"\n{BOLD}  ── Search Student ──{RESET}")
    print("  Search by: 1) Name   2) ID   3) Subject")
    mode = prompt("Choice", "1")

    if mode == "1":
        keyword = prompt("Name contains").lower()
        results = [s for s in students if keyword in s["name"].lower()]
    elif mode == "2":
        sid = get_int("Student ID", 1, 99999)
        results = [s for s in students if s["id"] == sid]
    elif mode == "3":
        keyword = prompt("Subject contains").lower()
        results = [s for s in students if keyword in s["subjects"].lower()]
    else:
        warn("Invalid choice.")
        return

    print_table(results, f"Search Results ({len(results)} found)")


# ── 4. EDIT ────────────────────────────────────────────────────────────────────
def edit_student(students: list[dict]) -> None:
    print(f"\n{BOLD}  ── Edit Student ──{RESET}")
    if not students:
        warn("No students on record.")
        return

    sid = get_int("Enter Student ID to edit", 1, 99999)
    target = next((s for s in students if s["id"] == sid), None)

    if target is None:
        err(f"No student found with ID {sid}.")
        return

    print(f"\n  Editing: {BOLD}{target['name']}{RESET}  (press Enter to keep current value)")
    print_table([target], "Current Record")

    new_name = prompt("New name", target["name"]).title() or target["name"]
    new_age  = get_int(f"New age", 5, 100, target["age"])
    raw_sub  = prompt("New subjects", target["subjects"])
    new_subjects = ", ".join(s.strip().title() for s in raw_sub.split(",") if s.strip()) or target["subjects"]
    new_marks = get_float("New average marks (0–100)", 0, 100, target["marks"])

    target.update({
        "name":     new_name,
        "age":      new_age,
        "subjects": new_subjects,
        "marks":    round(new_marks, 1),
    })
    save_students(students)
    ok(f"Student ID {sid} updated successfully. New grade: {grade(new_marks)}")


# ── 5. DELETE ──────────────────────────────────────────────────────────────────
def delete_student(students: list[dict]) -> None:
    print(f"\n{BOLD}  ── Delete Student ──{RESET}")
    if not students:
        warn("No students on record.")
        return

    sid = get_int("Enter Student ID to delete", 1, 99999)
    target = next((s for s in students if s["id"] == sid), None)

    if target is None:
        err(f"No student found with ID {sid}.")
        return

    print_table([target], "Student to Delete")
    confirm = prompt(f"Confirm delete '{target['name']}'? (y/n)", "n").lower()
    if confirm == "y":
        students.remove(target)
        save_students(students)
        ok(f"Student '{target['name']}' (ID {sid}) deleted.")
    else:
        info("Delete cancelled.")


# ── 6. SUMMARY / STATS ─────────────────────────────────────────────────────────
def show_summary(students: list[dict]) -> None:
    print(f"\n{BOLD}  ── Summary & Statistics ──{RESET}")
    if not students:
        warn("No records yet.")
        return

    total  = len(students)
    avg    = sum(s["marks"] for s in students) / total
    top    = max(students, key=lambda s: s["marks"])
    bottom = min(students, key=lambda s: s["marks"])

    grade_counts = {}
    for s in students:
        g = grade(s["marks"])
        grade_counts[g] = grade_counts.get(g, 0) + 1

    print(f"\n  {'─'*40}")
    print(f"  Total students   : {total}")
    print(f"  Class average    : {avg:.1f}  ({grade(avg)})")
    print(f"  Top performer    : {top['name']} ({top['marks']:.1f})")
    print(f"  Needs support    : {bottom['name']} ({bottom['marks']:.1f})")
    print(f"\n  Grade Distribution:")
    for g_label in ["A+","A","B","C","D","F"]:
        count = grade_counts.get(g_label, 0)
        bar   = "█" * count
        print(f"    {g_label:>2} : {bar} {count}")
    print(f"  {'─'*40}\n")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print_banner()
    info(f"Data file: {os.path.abspath(DATA_FILE)}")
    students = load_students()
    info(f"Loaded {len(students)} student record(s).\n")
    time.sleep(0.4)

    ACTIONS = {
        "1": add_student,
        "2": view_all,
        "3": search_student,
        "4": edit_student,
        "5": delete_student,
        "6": show_summary,
    }

    while True:
        print_menu()
        choice = prompt("Select option", "0")

        if choice == "0":
            print(f"\n  {BOLD}Goodbye! All records saved to {DATA_FILE}.{RESET}\n")
            break
        elif choice in ACTIONS:
            ACTIONS[choice](students)
        else:
            warn("Invalid option. Please choose 0–6.")


if __name__ == "__main__":
    main()
