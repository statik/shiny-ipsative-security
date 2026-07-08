"""Security culture survey — Shiny for Python port of the HavenGRC landing funnel.

Visitors take the ipsative Security Culture Diagnostic Survey (10 questions,
10 points each across four statements), their answers are stored in the
content database, and they see how their security culture profile compares
with the average of everyone who answered before them.
"""

from __future__ import annotations

import plotly.graph_objects as go
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

import db
import scds

# Series colors follow the app's chart palette: slot 1 (blue) is the current
# respondent, slot 2 (aqua) is the average of previous respondents.
YOU_COLOR = "#2a78d6"
YOU_FILL = "rgba(42, 120, 214, 0.25)"
OTHERS_COLOR = "#1baf7a"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"


def answer_input_id(question_index: int, category: str) -> str:
    return f"q{question_index}_{category.lower()}"


def question_panel(question_index: int) -> ui.nav_panel:
    question = scds.QUESTIONS[question_index]
    # Statements are shown without their category names, as in the original
    # survey, so respondents react to the descriptions rather than the labels.
    statement_rows = [
        ui.row(
            ui.column(
                3,
                ui.input_numeric(
                    answer_input_id(question_index, category),
                    None,
                    value=0,
                    min=0,
                    max=scds.POINTS_PER_QUESTION,
                    width="7em",
                ),
                class_="d-flex align-items-center",
            ),
            ui.column(9, ui.p(question["answers"][category])),
            class_="border-top py-3",
        )
        for category in scds.CATEGORIES
    ]
    return ui.nav_panel(
        None,
        ui.h4(
            f"Question {question_index + 1} of {scds.NUM_QUESTIONS}",
            class_="text-muted fs-6 mt-3",
        ),
        ui.h3(question["title"]),
        ui.p(scds.SURVEY_INSTRUCTIONS, class_="text-muted"),
        *statement_rows,
        ui.output_ui(f"q{question_index}_remaining"),
        ui.div(
            ui.input_action_button(
                f"back_{question_index}", "Back", class_="btn-outline-secondary me-2"
            ),
            ui.input_action_button(
                f"next_{question_index}",
                "Finish and see results"
                if question_index == scds.NUM_QUESTIONS - 1
                else "Next",
                class_="btn-primary",
            ),
            class_="my-4",
        ),
        value=f"q{question_index}",
    )


landing_panel = ui.nav_panel(
    None,
    ui.h1("How does your organization think about security?", class_="mt-4"),
    ui.p(
        "This is the Security Culture Diagnostic Survey (SCDS), a short "
        "ipsative survey that maps your organization onto four competing "
        "security cultures: Process, Compliance, Autonomy, and Trust."
    ),
    ui.p(
        f"You'll answer {scds.NUM_QUESTIONS} questions. "
        f"{scds.SURVEY_INSTRUCTIONS} There are no right or wrong answers — "
        "the survey measures which trade-offs your organization actually "
        "makes."
    ),
    ui.p(
        "When you finish, you'll see your security culture profile compared "
        "with everyone who has taken this survey before you."
    ),
    ui.output_ui("landing_count"),
    ui.input_action_button("start", "Start the survey", class_="btn-primary btn-lg my-3"),
    ui.p(
        ui.HTML(
            "The SCDS was created by Lance Hayden, Ph.D. "
            '(<a href="https://creativecommons.org/licenses/by-sa/4.0/">'
            "CC BY-SA 4.0</a>), and this app adapts the survey funnel from "
            '<a href="https://github.com/kindlyops/havengrc">HavenGRC</a>.'
        ),
        class_="text-muted small mt-4",
    ),
    value="landing",
)

results_panel = ui.nav_panel(
    None,
    ui.h2("Your security culture profile", class_="mt-4"),
    ui.output_ui("results_summary"),
    output_widget("results_chart"),
    ui.h4("Score details", class_="mt-4"),
    ui.output_ui("results_table"),
    ui.h4("What the categories mean", class_="mt-4"),
    ui.output_ui("category_help"),
    ui.input_action_button(
        "restart", "Take the survey again", class_="btn-outline-secondary my-4"
    ),
    value="results",
)

app_ui = ui.page_fixed(
    ui.navset_hidden(
        landing_panel,
        *[question_panel(i) for i in range(scds.NUM_QUESTIONS)],
        results_panel,
        id="wizard",
    ),
    title="Security Culture Survey",
)


def server(input, output, session):
    submission = reactive.value(None)  # dict with totals once submitted

    def allocation(question_index: int) -> dict[str, int]:
        return {
            category: int(input[answer_input_id(question_index, category)]() or 0)
            for category in scds.CATEGORIES
        }

    def remaining_points(question_index: int) -> int:
        return scds.POINTS_PER_QUESTION - sum(allocation(question_index).values())

    @render.ui
    def landing_count():
        submission.get()  # refresh the count after each new submission
        try:
            count = db.respondent_count()
        except Exception:
            return None
        if count == 0:
            return ui.p("Be the first to take the survey!", class_="fw-semibold")
        people = "person has" if count == 1 else "people have"
        return ui.p(f"{count} {people} taken the survey so far.", class_="fw-semibold")

    @reactive.effect
    @reactive.event(input.start)
    def _start():
        ui.update_navset("wizard", selected="q0")

    def register_question_handlers(question_index: int):
        @output(id=f"q{question_index}_remaining")
        @render.ui
        def _remaining():
            left = remaining_points(question_index)
            if left == 0:
                return ui.p("All 10 points assigned.", class_="text-success fw-semibold")
            if left < 0:
                return ui.p(
                    f"You've assigned {-left} too many points — remove some.",
                    class_="text-danger fw-semibold",
                )
            return ui.p(
                f"{left} of {scds.POINTS_PER_QUESTION} points left to assign.",
                class_="fw-semibold",
            )

        @reactive.effect
        @reactive.event(input[f"back_{question_index}"])
        def _back():
            target = "landing" if question_index == 0 else f"q{question_index - 1}"
            ui.update_navset("wizard", selected=target)

        @reactive.effect
        @reactive.event(input[f"next_{question_index}"])
        def _next():
            left = remaining_points(question_index)
            if left != 0:
                ui.notification_show(
                    f"Please assign exactly {scds.POINTS_PER_QUESTION} points "
                    "before continuing.",
                    type="warning",
                )
                return
            if question_index < scds.NUM_QUESTIONS - 1:
                ui.update_navset("wizard", selected=f"q{question_index + 1}")
            else:
                _submit()

    for i in range(scds.NUM_QUESTIONS):
        register_question_handlers(i)

    def _submit():
        answers = [allocation(i) for i in range(scds.NUM_QUESTIONS)]
        mine = {category: 0 for category in scds.CATEGORIES}
        for question_allocation in answers:
            for category, points in question_allocation.items():
                mine[category] += points
        try:
            submission_id = db.save_submission(answers)
            others_avg = db.average_category_totals(exclude_submission=submission_id)
            others_count = db.respondent_count(exclude_submission=submission_id)
        except Exception:
            ui.notification_show(
                "Your results are shown below, but they could not be saved "
                "to the shared database.",
                type="error",
                duration=10,
            )
            others_avg, others_count = {}, 0
        submission.set(
            {"mine": mine, "others_avg": others_avg, "others_count": others_count}
        )
        ui.update_navset("wizard", selected="results")

    @render.ui
    def results_summary():
        data = submission.get()
        if data is None:
            return None
        top = max(data["mine"], key=data["mine"].get)
        parts = [
            ui.p(
                ui.HTML(
                    f"Your strongest security culture is <b>{top}</b> "
                    f"({data['mine'][top]} of {scds.MAX_CATEGORY_POINTS} points)."
                )
            )
        ]
        if data["others_count"] > 0:
            people = (
                "1 previous respondent"
                if data["others_count"] == 1
                else f"{data['others_count']} previous respondents"
            )
            parts.append(
                ui.p(
                    f"The chart compares your profile with the average of {people}."
                )
            )
        else:
            parts.append(
                ui.p(
                    "You're the first respondent — as more people take the "
                    "survey, this page will compare your profile with theirs."
                )
            )
        return ui.div(*parts)

    @render_widget
    def results_chart():
        data = submission.get()
        if data is None:
            return go.FigureWidget()
        categories = scds.CATEGORIES
        closed = categories + categories[:1]
        mine = [data["mine"][c] for c in categories]
        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=mine + mine[:1],
                theta=closed,
                name="You",
                mode="lines+markers",
                line=dict(color=YOU_COLOR, width=2),
                marker=dict(size=8, color=YOU_COLOR),
                fill="toself",
                fillcolor=YOU_FILL,
                hovertemplate="You — %{theta}: %{r} points<extra></extra>",
            )
        )
        max_r = max(mine)
        if data["others_avg"]:
            others = [data["others_avg"].get(c, 0.0) for c in categories]
            max_r = max(max_r, *others)
            fig.add_trace(
                go.Scatterpolar(
                    r=others + others[:1],
                    theta=closed,
                    name="Previous respondents (avg)",
                    mode="lines+markers",
                    line=dict(color=OTHERS_COLOR, width=2, dash="dash"),
                    marker=dict(size=8, color=OTHERS_COLOR),
                    hovertemplate=(
                        "Previous respondents — %{theta}: %{r:.1f} points"
                        "<extra></extra>"
                    ),
                )
            )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    range=[0, max_r * 1.15],
                    gridcolor="#e6e5e1",
                    tickfont=dict(color=TEXT_SECONDARY, size=11),
                ),
                angularaxis=dict(
                    gridcolor="#e6e5e1",
                    tickfont=dict(color=TEXT_PRIMARY, size=13),
                ),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0),
            font=dict(color=TEXT_PRIMARY),
            margin=dict(t=40, b=40),
            height=440,
        )
        return fig

    @render.ui
    def results_table():
        data = submission.get()
        if data is None:
            return None
        has_others = bool(data["others_avg"])
        header = [ui.tags.th("Category"), ui.tags.th("Your points")]
        if has_others:
            header += [ui.tags.th("Previous respondents (avg)"), ui.tags.th("Difference")]
        rows = []
        for category in scds.CATEGORIES:
            mine = data["mine"][category]
            cells = [ui.tags.td(category), ui.tags.td(mine)]
            if has_others:
                avg = data["others_avg"].get(category, 0.0)
                diff = mine - avg
                cells += [
                    ui.tags.td(f"{avg:.1f}"),
                    ui.tags.td(f"{diff:+.1f}"),
                ]
            rows.append(ui.tags.tr(*cells))
        return ui.tags.table(
            ui.tags.thead(ui.tags.tr(*header)),
            ui.tags.tbody(*rows),
            class_="table table-striped w-auto",
        )

    @render.ui
    def category_help():
        return ui.tags.dl(
            *[
                item
                for category in scds.CATEGORIES
                for item in (
                    ui.tags.dt(category),
                    ui.tags.dd(scds.CATEGORY_DESCRIPTIONS[category]),
                )
            ]
        )

    @reactive.effect
    @reactive.event(input.restart)
    def _restart():
        submission.set(None)
        for i in range(scds.NUM_QUESTIONS):
            for category in scds.CATEGORIES:
                ui.update_numeric(answer_input_id(i, category), value=0)
        ui.update_navset("wizard", selected="landing")


app = App(app_ui, server)
