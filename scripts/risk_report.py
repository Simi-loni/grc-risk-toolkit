"""
RISK REPORT

What this does
  Reads a risk register (CSV), works out each risk's score and rating,
  and flags problems a risk or compliance lead would want to know about.

How scoring works
  Score = likelihood x impact, each from 1 to 5. See METHODOLOGY.md for the
  scales, the rating bands and the example risk tolerance.

What it flags
  1. Overdue: a risk that is not closed and is past its due date.
  2. No treatment plan: a risk above tolerance with no owner or no due date,
     unless it is being accepted.
  3. Unsigned acceptance: a risk above tolerance that is being accepted
     without a named person in accepted_by.

Limitations
  The likelihood and impact numbers are judgments made by people. This
  script checks the arithmetic and the follow-through, not whether the
  scores are right. It also does not check that the register is complete.

Built with AI assistance. Written by a GRC practitioner learning to code.
"""

import csv
import sys
from datetime import date

RISK_TOLERANCE = 10  # risks at or above this need a treatment plan


def load_register(path):
    """Read the risk register and return a list of rows."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


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
    if risk["status"] == "closed":
        return flags  # closed risks are not chased

    due = risk["due_date"].strip()
    if due != "" and date.fromisoformat(due) < as_of:
        days_late = (as_of - date.fromisoformat(due)).days
        flags.append(f"overdue by {days_late} days")

    if score >= RISK_TOLERANCE:
        if risk["treatment"] == "accept":
            if risk["accepted_by"].strip() == "":
                flags.append("above tolerance, accepted without sign-off")
        else:
            if risk["owner"].strip() == "" or due == "":
                flags.append("above tolerance, no owner or due date")
    return flags


def main(path, as_of):
    register = load_register(path)
    rows = []
    for risk in register:
        score = int(risk["likelihood"]) * int(risk["impact"])
        rows.append((risk, score, find_flags(risk, score, as_of)))
    rows.sort(key=lambda r: r[1], reverse=True)

    open_rows = [r for r in rows if r[0]["status"] != "closed"]
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
