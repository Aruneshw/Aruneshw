#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint (the same fragment the profile page itself uses) and
write data/contributions.json with the raw days plus derived stats
(current streak, longest streak, best day, monthly totals).

No token, no auth, no GraphQL -- just the public HTML GitHub already serves.
Refreshed approximately every 15 minutes by GitHub Actions.
"""
import datetime
import json
import os
import re
from bs4 import BeautifulSoup
from github_data import github_session

USERNAME = os.environ.get("GH_PROFILE_USER", "Aruneshw")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    with github_session(authenticated=False) as session:
        resp = session.get(URL, headers={"Accept": "text/html"}, timeout=30)
        resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        raise ValueError("No calendar cells found; GitHub markup may have changed")

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"([\d,]+)\s+contributions?\b", text, re.I)
            if not m:
                raise ValueError(f"Cannot read contribution count for {date}: {text!r}")
            count = int(m.group(1).replace(",", ""))
        days.append({"date": date, "count": count, "level": int(td.get("data-level") or 0)})

    days.sort(key=lambda d: d["date"])
    validate_days(days)
    today = datetime.datetime.now(datetime.timezone.utc).date()
    last = datetime.date.fromisoformat(days[-1]["date"])
    if not 350 <= len(days) <= 371 or not today - datetime.timedelta(days=1) <= last <= today:
        raise ValueError("GitHub returned an incomplete or stale contribution calendar")
    return days


def validate_days(days):
    if not days:
        raise ValueError("The contribution calendar is empty")
    previous = None
    for day in days:
        date = datetime.date.fromisoformat(day["date"])
        if previous is not None and date - previous != datetime.timedelta(days=1):
            raise ValueError("Contribution dates must be unique and consecutive")
        if not isinstance(day["count"], int) or day["count"] < 0:
            raise ValueError("Contribution counts must be nonnegative integers")
        previous = date


def compute_current_streak(days, today=None):
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    idx = len(days) - 1
    last = datetime.date.fromisoformat(days[idx]["date"])
    if last < today - datetime.timedelta(days=1):
        return 0, None, None
    if last == today and days[idx]["count"] == 0:
        idx -= 1  # today isn't over yet -- don't break the streak on it
    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    start_idx = idx + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days):
    longest = run = 0
    longest_start = longest_end = None
    run_start_idx = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = days[i]["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days, today=None):
    validate_days(days)
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"])
    cur_len, cur_start, cur_end = compute_current_streak(days, today=today)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    return {
        "username": USERNAME,
        "source": URL,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


if __name__ == "__main__":
    days = fetch_days()
    data = build_data(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT_PATH}: {data['total_contributions']} contributions, "
          f"current streak {data['current_streak']['length']}, "
          f"longest streak {data['longest_streak']['length']}")
