import json
import math
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

DEFAULTS = {
    "dev_hours_per_day": 8,
    "pro_window_ai_hours": 2.0,
    "budget_share": 0.8,
    "windows_per_day": 2,
    "window_clock_hours": 5,
}
OVERHEAD = {"planning": 0.08, "fixes": 0.12}
TIERS = [("Pro", 1), ("Max 100", 5), ("Max 200", 20)]
OWNERS = ("AI", "Developer")

BOLD = Font(bold=True)
HEADER_FILL = PatternFill("solid", fgColor="D9D9D9")
SECTION_FILL = PatternFill("solid", fgColor="EEF3F8")
OWNER_FILL = {"AI": PatternFill("solid", fgColor="E2EFDA"), "Developer": PatternFill("solid", fgColor="FCE4D6")}
INPUT_FONT = Font(color="0000FF")
TOP = Border(top=Side(style="thin"))
WRAP = Alignment(wrap_text=True, vertical="top")


def validate(rows):
    for i, r in enumerate(rows):
        if "section" in r:
            continue
        if r.get("owner") not in OWNERS:
            sys.exit(f"row {i} '{r.get('name')}': owner must be one of {OWNERS}")
        if not 0 <= r["min"] <= r["max"]:
            sys.exit(f"row {i} '{r['name']}': need 0 <= min <= max")


def uncalibrated(rows):
    area, total, per_area = None, 0.0, {}
    for r in rows:
        if "section" in r:
            area = r.get("uncalibrated")
            continue
        total += r["max"]
        if area:
            per_area[area] = per_area.get(area, 0.0) + r["max"]
    if not per_area:
        return None
    return list(per_area), sum(per_area.values()) / total


def append_section(ws, title, comment=None):
    ws.append([title, None, None, None, comment])
    for c in ws[ws.max_row][:5]:
        c.font = BOLD
        c.fill = SECTION_FILL


def append_task(ws, name, lo, hi, owner, comment=None):
    ws.append([name, lo, hi, owner, comment or None])
    ws.cell(ws.max_row, 4).fill = OWNER_FILL[owner]


def build_estimate_sheet(ws, rows, overhead):
    ws.title = "Estimate"
    ws.append(["Task / Feature", "Min, h", "Max, h", "Who", "Comment"])
    for c in ws[1]:
        c.font = BOLD
        c.fill = HEADER_FILL
    for r in rows:
        if "section" in r:
            append_section(ws, r["section"], r.get("comment"))
        else:
            append_task(ws, r["name"], r["min"], r["max"], r["owner"], r.get("comment"))

    if overhead:
        feat = ws.max_row
        share = overhead["planning"] + overhead["fixes"]
        append_section(ws, "Overhead", f"{share:.0%} of AI feature hours: the reference project's planning, fix and tooling sessions "
                                       "no feature owned were ~20% of all AI time.")
        for name, key in (("Planning & specs", "planning"), ("Fixes & integration", "fixes")):
            f = [f'=ROUND(SUMIF($D$2:$D${feat},"AI",{col}$2:{col}${feat})*{overhead[key]},1)' for col in "BC"]
            append_task(ws, name, f[0], f[1], "AI")

    last = ws.max_row
    who = DataValidation(type="list", formula1='"AI,Developer"', allow_blank=True)
    ws.add_data_validation(who)
    who.add(f"D2:D{last}")

    totals = {}
    for offset, (label, crit) in enumerate((("Total", None), ("Developer", "Developer"), ("AI", "AI")), start=2):
        row = last + offset
        if crit is None:
            f_min, f_max = f"=SUM(B2:B{last})", f"=SUM(C2:C{last})"
        else:
            f_min = f'=SUMIF($D$2:$D${last},"{crit}",B$2:B${last})'
            f_max = f'=SUMIF($D$2:$D${last},"{crit}",C$2:C${last})'
        for col, value in enumerate((label, f_min, f_max), start=1):
            ws.cell(row, col, value).font = BOLD
        totals[label] = row
    for col in range(1, 6):
        ws.cell(totals["Total"], col).border = TOP

    for row in ws.iter_rows(min_row=2, min_col=2, max_col=3):
        for c in row:
            c.number_format = "0.0"
    for row in ws.iter_rows(min_row=2, max_col=5):
        for c in row:
            c.alignment = WRAP
    ws.column_dimensions["A"].width = 52
    ws.column_dimensions["B"].width = 9
    ws.column_dimensions["C"].width = 9
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 70
    ws.freeze_panes = "A2"
    return totals


def build_schedule_sheet(ws, a, totals, gaps):
    ws["A1"] = "Assumptions (edit blue cells)"
    ws["A1"].font = BOLD
    inputs = [
        ("Developer hours per working day", "dev_hours_per_day"),
        ("Pro: AI hours per 5h window at 100% budget", "pro_window_ai_hours"),
        ("Share of window budget used", "budget_share"),
        ("5h windows per working day", "windows_per_day"),
        ("Max AI hours a window can yield (clock)", "window_clock_hours"),
    ]
    for i, (label, key) in enumerate(inputs, start=2):
        ws.cell(i, 1, label)
        ws.cell(i, 2, a[key]).font = INPUT_FONT
    dev_day, pro_win, share, windows, clock = "$B$2", "$B$3", "$B$4", "$B$5", "$B$6"

    head = 8
    ws.cell(head, 1, "Tier")
    for col, title in enumerate(["Budget vs Pro", "AI h / window", "AI h / day",
                                 "Working days min", "Working days max", "Weeks min", "Weeks max"], start=2):
        ws.cell(head, col, title)
    for c in ws[head][:8]:
        c.font = BOLD
        c.fill = HEADER_FILL

    ai_min, ai_max = f"Estimate!B{totals['AI']}", f"Estimate!C{totals['AI']}"
    all_min, all_max = f"Estimate!B{totals['Total']}", f"Estimate!C{totals['Total']}"
    for i, (tier, mult) in enumerate(TIERS, start=head + 1):
        ws.cell(i, 1, tier)
        ws.cell(i, 2, mult).font = INPUT_FONT
        ws.cell(i, 3, f"=MIN({clock},{pro_win}*B{i}*{share})").number_format = "0.0"
        ws.cell(i, 4, f"=C{i}*{windows}").number_format = "0.0"
        ws.cell(i, 5, f"=ROUNDUP(MAX({ai_min}/D{i},{all_min}/{dev_day}),0)")
        ws.cell(i, 6, f"=ROUNDUP(MAX({ai_max}/D{i},{all_max}/{dev_day}),0)")
        ws.cell(i, 7, f"=E{i}/5").number_format = "0.0"
        ws.cell(i, 8, f"=F{i}/5").number_format = "0.0"

    note = head + len(TIERS) + 2
    ws.cell(note, 1, "Working days only; weekends, holidays and weekly usage caps are not counted. "
                     "AI rows include the developer's prompting and review time. "
                     "Days = max(AI hours / AI capacity per day, all hours / developer hours per day).")
    ws.cell(note, 1).alignment = WRAP
    ws.merge_cells(start_row=note, start_column=1, end_row=note, end_column=8)
    ws.row_dimensions[note].height = 45

    if gaps:
        areas, share = gaps
        lead = "LOW CONFIDENCE: most" if share > 0.5 else "Part"
        warn = note + 1
        ws.cell(warn, 1, f"{lead} of the estimate ({share:.0%} of feature max hours) is in areas the calibration never measured: "
                         f"{', '.join(areas)}. Those rows use judgment multipliers, not measured rates.")
        ws.cell(warn, 1).font = Font(bold=True, color="C00000")
        ws.cell(warn, 1).alignment = WRAP
        ws.merge_cells(start_row=warn, start_column=1, end_row=warn, end_column=8)
        ws.row_dimensions[warn].height = 45
    ws.column_dimensions["A"].width = 44
    for col in "BCDEFGH":
        ws.column_dimensions[col].width = 15


def summarize(rows, a, overhead):
    tot = {k: [0.0, 0.0] for k in OWNERS}
    for r in rows:
        if "section" not in r:
            tot[r["owner"]][0] += r["min"]
            tot[r["owner"]][1] += r["max"]
    if overhead:
        share = overhead["planning"] + overhead["fixes"]
        tot["AI"] = [round(v * overhead["planning"], 1) + round(v * overhead["fixes"], 1) + v for v in tot["AI"]]
        print(f"Overhead {share:.0%} of AI feature hours included")
    print(f"Total   {tot['AI'][0] + tot['Developer'][0]:.1f} - {tot['AI'][1] + tot['Developer'][1]:.1f} h")
    print(f"  Developer {tot['Developer'][0]:.1f} - {tot['Developer'][1]:.1f} h")
    print(f"  AI        {tot['AI'][0]:.1f} - {tot['AI'][1]:.1f} h")
    for tier, mult in TIERS:
        per_day = min(a["window_clock_hours"], a["pro_window_ai_hours"] * mult * a["budget_share"]) * a["windows_per_day"]
        days = [math.ceil(max(tot["AI"][i] / per_day, (tot["AI"][i] + tot["Developer"][i]) / a["dev_hours_per_day"]))
                for i in (0, 1)]
        print(f"{tier:8} {per_day:.1f} AI h/day -> {days[0]} - {days[1]} working days")


def main(path):
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    a = {**DEFAULTS, **spec.get("assumptions", {})}
    overhead = spec.get("overhead", True)
    overhead = {**OVERHEAD, **overhead} if isinstance(overhead, dict) else (OVERHEAD if overhead else None)
    rows = spec["rows"]
    validate(rows)

    wb = Workbook()
    totals = build_estimate_sheet(wb.active, rows, overhead)
    gaps = uncalibrated(rows)
    build_schedule_sheet(wb.create_sheet("Schedule"), a, totals, gaps)
    wb.save(spec["output"])
    print(f"Saved {spec['output']}")
    summarize(rows, a, overhead)
    if gaps:
        print(f"Uncalibrated: {', '.join(gaps[0])} = {gaps[1]:.0%} of feature max hours")


if __name__ == "__main__":
    main(sys.argv[1])
