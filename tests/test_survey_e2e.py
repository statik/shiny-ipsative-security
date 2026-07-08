"""End-to-end test of the survey funnel, driven with Playwright.

Walks the full flow — landing page, point-allocation validation, all ten
questions, submission, and the results comparison — against a live server
seeded with one prior respondent. Also captures the screenshots embedded in
the README (set SCREENSHOT_DIR to change or disable isn't needed; they are
overwritten on each run).
"""

import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

CATEGORIES = ["process", "compliance", "autonomy", "trust"]
POINTS = [4, 3, 2, 1]
SCREENSHOT_DIR = Path(
    os.environ.get(
        "SCREENSHOT_DIR", Path(__file__).resolve().parent.parent / "screenshots"
    )
)


def _launch_chromium(playwright):
    # In CI, `playwright install chromium` provides the browser. In sandboxes
    # with a pre-installed Chromium, fall back to the known executable path.
    try:
        return playwright.chromium.launch()
    except Exception:
        return playwright.chromium.launch(
            executable_path="/opt/pw-browsers/chromium"
        )


def _shot(page, name: str) -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=SCREENSHOT_DIR / name, full_page=True)


def test_full_survey_flow(app_url):
    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page(viewport={"width": 1100, "height": 900})
        page.goto(app_url, wait_until="networkidle")

        # Landing page shows the seeded respondent count
        expect(page.locator("h1")).to_contain_text(
            "How does your organization think about security?"
        )
        expect(page.locator("#landing_count")).to_contain_text(
            "1 person has taken the survey so far."
        )
        _shot(page, "landing.png")
        page.click("#start")

        # Advancing without allocating all 10 points is rejected
        active = page.locator(".tab-pane.active")
        expect(active).to_contain_text("Question 1 of 10")
        page.click("#next_0")
        expect(page.locator(".shiny-notification")).to_contain_text(
            "Please assign exactly 10 points"
        )
        page.click(".shiny-notification-close")
        expect(page.locator(".shiny-notification")).to_have_count(0)

        for i in range(10):
            expect(active).to_contain_text(f"Question {i + 1} of 10")
            for category, points in zip(CATEGORIES, POINTS):
                page.fill(f"#q{i}_{category}", str(points))
                page.dispatch_event(f"#q{i}_{category}", "change")
            expect(active.locator(f"#q{i}_remaining")).to_contain_text(
                "All 10 points assigned."
            )
            if i == 0:
                _shot(page, "question.png")
            page.click(f"#next_{i}")

        # Results: summary, radar chart, and comparison table
        expect(page.locator("h2")).to_contain_text(
            "Your security culture profile", timeout=15000
        )
        summary = page.locator("#results_summary")
        expect(summary).to_contain_text(
            "Your strongest security culture is Process (40 of 100 points)."
        )
        expect(summary).to_contain_text(
            "the average of 1 previous respondent"
        )
        expect(page.locator("#results_chart .plotly")).to_be_visible(
            timeout=15000
        )
        table = page.locator("#results_table table")
        expect(table).to_contain_text("Previous respondents (avg)")
        # Seeded respondent: Process 40, Compliance 20, Autonomy 10, Trust 30
        expect(table.locator("tr", has_text="Compliance")).to_contain_text(
            "+10.0"
        )
        page.wait_for_timeout(500)  # let the chart animation settle
        _shot(page, "results.png")

        # Restart returns to the landing page with a refreshed count
        page.click("#restart")
        expect(page.locator("#landing_count")).to_contain_text(
            "2 people have taken the survey so far."
        )
        browser.close()
