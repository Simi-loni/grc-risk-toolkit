"""
RISK REPORT

What this does
  Reads a risk register (CSV), works out each risk's score and rating from
  likelihood and impact, and flags problems a risk or compliance lead would
  want to know about.

Two file layouts are understood, and the script picks the right one from the
header row:
  1. data/risk_register.csv, the small test file.
  2. data/novaprotect_risk_register.csv, the portfolio register exported from
     a spreadsheet. It has no treatment column, so every risk is treated as
     "mitigate" because each one has a mitigation action.

How scoring works
  Score = likelihood x impact, each from 1 to 5. See METHODOLOGY.md for the
  scales, the rating bands and the example risk tolerance.

What it flags
  1. Rating mismatch: the rating in the file does not match the score. The
     script uses its own bands, so a hand-typed or stale rating shows up.
  2. Overdue: a risk that is not closed and is past its target date.
  3. Review overdue: the next review date has passed.
  4. No treatment plan: a risk above tolerance with no owner or no date,
     unless it is being accepted.
  5. Not started: a risk above tolerance, not being accepted, where the
     status says work has not started.
  6. Unsigned acceptance: a risk above tolerance that is being accepted
     without a named person in accepted_by.

Dates
  Dates must be written YYYY-MM-DD. Day Mon YYYY and MM/DD/YYYY are also
  accepted. If a spreadsheet exports dates another way, the script stops and
  says which value it could not read.

Limitations
  The likelihood and impact numbers are judgments made by people. This
  script checks the arithmetic and the follow-through, not whether the
  scores are right. It also does not check that the register is complete.

Built with AI assistance. Written by a GRC practitioner learning to code.
"""

import csv
import sys
from datetime import date, datetime

RISK_TOLERANCE = 10  # risks at or above this need a treatment plan
NOT_STARTED = ("open", "not started")
DATE_FORMATS = ("%Y-%m-%d", "%d %b %Y", "%m/%d/%Y")

# Column names in each file layout. None means the file has no such column.
LAYOUTS = {
    "simple": {
        "id": "id", "risk": "risk", "likelihood": "likelihood",
        "impact": "impact", "owner": "owner", "treatment": "treatment",
        "status": "status", "due": "due_date", "accepted_by": "accepted_by",
        "rating": None, "next_review": None,
    },
    "novaprotect": {
        "id": "Risk ID", "risk": "Risk Description",
        "likelihood": "Likelihood (1-5)", "impact": "Impact (1-5)",
        "owner": "Risk Owner", "treatment": None, "status": "Status",
        "due": "Target Date", "accepted_by": None,
        "rating": "Risk Rating", "next_review": "Next Review",
    },
}


def parse_date(text):
    """Turn a date written in the file into a date, or None if blank."""
    text = text.strip()
    if text == "":
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    sys.exit(f"Could not read the date '{text}'. Use YYYY-MM-DD.")


def load_register(path):
    """Read the file and return risks with the same field names every time."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if "Risk ID" in headers:
            layout = LAYOUTS["novaprotect"]
            default_treatment = "mitigate"
        elif "id" in headers:
            layout = LAYOUTS["simple"]
            default_treatment = ""
        else:
            sys.exit("This file's columns are not ones the script knows.")
        risks = []
        for row in reader:
            def get(key):
                column = layout[key]
                return row[column].strip() if column else ""
            risks.append({
                "id": get("id"),
                "risk": get("risk"),
                "likelihood": int(get("likelihood")),
                "impact": int(get("impact")),
                "owner": get("owner"),
                "treatment": get("treatment") or default_treatment,
                "status": get("status"),
                "due": parse_date(get("due")),
                "accepted_by": get("accepted_by"),
                "rating": get("rating"),
                "next_review": parse_date(get("next_review")),
            })
    return risks


def rating(score):
    """Turn a score into a rating. Bands match METHODOLOGY.md."""
    if score >= 15:
        return "Critical"
    if score >= 10:
        return "High"
    if score >= 5:
        return "Medium"
    return "Low"


def find_flags(risk, score, as_of):
    """Return a list of problems with this risk. Empty means none."""
    flags = []

    if risk["rating"] and risk["rating"].lower() != rating(score).lower():
        flags.append(
            f"rating in file is {risk['rating']}, but score {score} is {rating(score)}"
        )

    if risk["status"].lower() == "closed":
        return flags  # closed risks are not chased for follow-up

    if risk["due"] and risk["due"] < as_of:
        flags.append(f"overdue by {(as_of - risk['due']).days} days")

    if risk["next_review"] and risk["next_review"] < as_of:
        flags.append(f"review overdue by {(as_of - risk['next_review']).days} days")

    if score >= RISK_TOLERANCE:
        if risk["treatment"] == "accept":
            if risk["accepted_by"] == "":
                flags.append("above tolerance, accepted without sign-off")
        else:
            if risk["owner"] == "" or risk["due"] is None:
                flags.append("above tolerance, no owner or due date")
            if risk["status"].lower() in NOT_STARTED:
                flags.append("above tolerance, work not started")
    return flags


def main(path, as_of):
    register = load_register(path)
    rows = []
    for risk in register:
        score = risk["likelihood"] * risk["impact"]
        rows.append((risk, score, find_flags(risk, score, as_of)))
    rows.sort(key=lambda r: r[1], reverse=True)

    open_rows = [r for r in rows if r[0]["status"].lower() != "closed"]
    print(f"Risk report, as of {as_of}")
    print(f"Risks in register: {len(rows)} ({len(open_rows)} not closed)")
    print(f"Risk tolerance: score {RISK_TOLERANCE} or above")
    print()
    for rating_name in ["Critical", "High", "Medium", "Low"]:
        count = sum(1 for r in open_rows if rating(r[1]) == rating_name)
        print(f"  {rating_name}: {count}")
    print()
    print("Open risks, highest score first:")
    for risk, score, flags in open_rows:
        print(f"  {risk['id']} [{score} {rating(score)}] {risk['risk']}")
        print(f"      owner {risk['owner']}, {risk['treatment']}, {risk['status']}")
        for flag in flags:
            print(f"      FLAG: {flag}")

    flagged = [r for r in rows if r[2]]
    print()
    if not flagged:
        print("RESULT: No flags.")
        return 0
    print(f"RESULT: {len(flagged)} risk(s) need attention.")
    return 1


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/risk_register.csv"
    if len(sys.argv) > 2:
        as_of_date = date.fromisoformat(sys.argv[2])
    else:
        as_of_date = date.today()
    sys.exit(main(csv_path, as_of_date))
