# grc-risk-toolkit

Risk scoring and register tooling for GRC. A simple 5 x 5 method, a sample risk register, and a report that flags overdue risks and unsigned risk acceptances.

## About this project

I work in GRC and I am learning to code. I built this with AI assistance (Claude) and worked through the script until I could explain it myself. The part I care about is the method: how a risk gets scored, what counts as above tolerance, and who is allowed to accept it. The code only applies those rules consistently.

All data in this repo is made-up sample data. No real company information is used.

## What is here

| File | Purpose |
|---|---|
| METHODOLOGY.md | Likelihood and impact scales, rating bands, example risk tolerance, treatment options |
| data/risk_register.csv | Sample register with owners, treatments, status and due dates |
| scripts/risk_report.py | Scores each risk and flags problems |
| WORKED_EXAMPLE.md | A risk assessment of a new webhook feature, from scoring to a recommendation for leadership |
| data/novaprotect_risk_register.csv | Portfolio sample: 15-risk register for a fictional organisation |
## Portfolio sample

data/novaprotect_risk_register.csv is a 15 risk enterprise risk register I built as a portfolio project for a fictional organization, NovaProtect. All risks, owners and dates are invented. I designed the register. I used AI assistance to check my scoring against my own rating bands and fix the errors it found, and to add the status and target date columns.

data/risk_register.csv is a smaller file used only to test the script.

The full portfolio, including a FedRAMP crosswalk, an audit program and a vendor assessment, is here (https://drive.google.com/drive/folders/1J4H7y9-mTc4oFsQRK_wbOLpDfvlfq2n0)

## How to run it

You need Python 3 installed.

```
python3 scripts/risk_report.py data/risk_register.csv 2026-11-23
python3 scripts/risk_report.py data/novaprotect_risk_register.csv 2026-11-23
```

The date at the end is the "as of" date. The sample data was built around it. Without it, the script uses today's date and more risks will show as overdue.

## What the report flags

1. A rating in the file that does not match the score.
2. A risk that is not closed and is past its target date.
3. A risk whose next review date has passed.
4. A risk above tolerance with no owner or no date.
5. A risk above tolerance with work not started.
6. A risk above tolerance that is being accepted without a named person signing it off.

## Choices in the method

The scales, the rating bands and the tolerance (a score of 10 or above) are examples. They are written down in METHODOLOGY.md so a company can change them to match its own risk policy. I chose the 10 line because a score of 10 means something like "possible and major" or "likely and moderate", which is where I would expect a treatment plan.

## What this does not do

The likelihood and impact numbers are judgments made by people. The script checks the arithmetic and the follow-through. It does not check whether the scores are right or whether the register is complete. A real risk process also needs the conversation with the owner.
