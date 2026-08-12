import json
from pathlib import Path


PORTFOLIO_PATH = Path(
    "outputs/ai_deployment_portfolio.json"
)

RECOMMENDATIONS_PATH = Path(
    "outputs/deployment_recommendations.json"
)

OUTPUT_PATH = Path(
    "outputs/executive_ai_report.md"
)


def load_json(path):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def format_list(items):
    if not items:
        return "- Not specified"

    return "\n".join(
        f"- {item}"
        for item in items
    )


def decision_label(decision):
    labels = {
        "Pilot Now": "🟢 PILOT NOW",
        "Pilot Next": "🟡 PILOT NEXT",
        "Validate Further": "🔵 VALIDATE FURTHER",
        "Specialized Review": "🟣 SPECIALIZED REVIEW",
        "Backlog": "⚪ BACKLOG"
    }

    return labels.get(
        decision,
        decision
    )


def build_executive_summary(
    portfolio,
    summary
):
    top = portfolio[:3]

    return f"""
## Executive Summary

The analysis identified **{summary.get('total_opportunities', 0)} canonical AI opportunities**
from the customer conversation dataset.

The opportunity discovery pipeline consolidated recurring workflows into a
prioritized deployment portfolio.

### Portfolio Recommendation

- **Pilot Now:** {summary.get('pilot_now', 0)}
- **Pilot Next:** {summary.get('pilot_next', 0)}
- **Validate Further:** {summary.get('validate_further', 0)}
- **Specialized Review:** {summary.get('specialized_review', 0)}
- **Backlog:** {summary.get('backlog', 0)}

### Highest-Priority Opportunities

{format_list([
    item["opportunity_name"]
    for item in top
])}

The portfolio should be treated as a deployment planning framework rather
than a commitment to immediate enterprise-wide rollout.

Pilot decisions should be validated against customer stakeholders,
available data, integration feasibility, security requirements, and
measurable business outcomes.
"""


def build_portfolio_table(portfolio):
    lines = [
        "## AI Opportunity Portfolio",
        "",
        "| Opportunity | Score | Impact | Complexity | Risk | Decision | Pilot Team |",
        "|---|---:|---|---|---|---|---|"
    ]

    for item in portfolio:
        pilot_team = (
            item.get("pilot_team")
            or "Not specified"
        )

        lines.append(
            "| "
            + item["opportunity_name"]
            + " | "
            + str(item["adjusted_score"])
            + " | "
            + item["impact"]
            + " | "
            + item["complexity"]
            + " | "
            + item["deployment_risk"]
            + " | "
            + item["deployment_decision"]
            + " | "
            + pilot_team
            + " |"
        )

    return "\n".join(lines)


def build_opportunity_section(
    item,
    recommendation
):
    name = item["opportunity_name"]

    target_personas = recommendation.get(
        "target_personas",
        []
    )

    required_data_sources = recommendation.get(
        "required_data_sources",
        []
    )

    integrations = recommendation.get(
        "likely_integrations",
        []
    )

    security = recommendation.get(
        "security_considerations",
        []
    )

    adoption = recommendation.get(
        "adoption_strategy",
        []
    )

    expansion = recommendation.get(
        "expansion_criteria",
        []
    )

    recommended_workflow = recommendation.get(
        "recommended_ai_workflow",
        "Not specified"
    )

    deployment_recommendation = item.get(
        "deployment_recommendation",
        "Not specified"
    )

    human_in_loop = item.get(
        "human_in_the_loop",
        "Not specified"
    )

    return f"""
---

## {name}

### Deployment Decision

**{decision_label(item['deployment_decision'])}**

**Adjusted Score:** {item['adjusted_score']}/100

**Original Opportunity Score:** {item['original_score']}/100

### Impact / Complexity / Risk

- **Impact:** {item['impact']}
- **Complexity:** {item['complexity']}
- **Deployment Risk:** {item['deployment_risk']}
- **Deployment Readiness:** {item['deployment_readiness']}/100

### Recommended Deployment Approach

{deployment_recommendation}

### Pilot

**Team:** {item.get('pilot_team') or 'Not specified'}

**Duration:** {item.get('pilot_duration') or 'Not specified'}

### Target Personas

{format_list(target_personas)}

### Required Data Sources

{format_list(required_data_sources)}

### Likely Integrations

{format_list(integrations)}

### Recommended AI Workflow

{recommended_workflow}

### Human-in-the-Loop

{human_in_loop}

### Security Considerations

{format_list(security)}

### Adoption Strategy

{format_list(adoption)}

### Success Metrics

{format_list(item.get('success_metrics', []))}

### Expansion Criteria

{format_list(expansion)}

### Deployment Blockers

{format_list(item.get('deployment_blockers', []))}
"""


def build_roadmap(portfolio):
    pilot_now = [
        x for x in portfolio
        if x["deployment_decision"] == "Pilot Now"
    ]

    pilot_next = [
        x for x in portfolio
        if x["deployment_decision"] == "Pilot Next"
    ]

    validate = [
        x for x in portfolio
        if x["deployment_decision"] == "Validate Further"
    ]

    first_pilot = (
        pilot_now[:1]
        if pilot_now
        else pilot_next[:1]
    )

    second_wave = pilot_next[1:4]

    final_wave = (
        pilot_next[4:]
        + validate
    )

    return f"""
## Suggested 90-Day Roadmap

### Days 0–30: Select and Launch the First Pilot

Prioritize the highest-scoring opportunity ready for an initial pilot.

{format_list([
    x["opportunity_name"]
    for x in first_pilot
])}

Recommended activities:

- Confirm the pilot team and executive sponsor.
- Establish baseline business and workflow metrics.
- Validate required data access.
- Confirm security and governance requirements.
- Define human approval points.
- Launch a controlled pilot.
- Establish a weekly pilot review cadence.

### Days 31–60: Launch the Second Wave

Expand into additional opportunities classified as **Pilot Next**.

{format_list([
    x["opportunity_name"]
    for x in second_wave
])}

Recommended activities:

- Review results from the first pilot.
- Launch the next controlled pilots.
- Compare AI-assisted performance against baseline metrics.
- Capture user feedback and adoption signals.
- Refine workflows and human-review requirements.

### Days 61–90: Validate and Prepare for Scale

Focus on remaining **Pilot Next** opportunities and opportunities
classified as **Validate Further**.

{format_list([
    x["opportunity_name"]
    for x in final_wave
])}

Recommended activities:

- Evaluate pilot outcomes.
- Identify opportunities ready for broader deployment.
- Reassess implementation complexity and risk.
- Validate security and governance requirements.
- Define expansion criteria for successful pilots.
- Build the next-quarter deployment roadmap.
"""


def build_evidence_section():
    return """
## Evidence vs. Recommendation

**Evidence** refers to workflows, pain points, frequency, and other
information identified from the customer conversations.

**Recommendations** are proposed deployment actions generated from that
evidence. They represent hypotheses for customer validation and should not
be interpreted as confirmed customer requirements.

**Assumptions** are deployment conditions that should be validated with the
customer before implementation, including data availability, integrations,
pilot-team availability, security requirements, and expected adoption.
"""


def build_methodology_section():
    return """
## Methodology

This assessment follows a multi-stage workflow:

1. Customer conversations were analyzed to identify recurring human workflows.
2. Related workflows were grouped using semantic similarity.
3. Workflow clusters were synthesized into canonical AI opportunities.
4. Opportunities were scored using evidence and AI suitability.
5. Claude generated deployment recommendations for each opportunity.
6. A deterministic portfolio model evaluated impact, complexity, risk, and readiness.
7. Opportunities were classified into deployment decisions.

The resulting portfolio is intended to support customer discovery,
prioritization, pilot planning, and deployment discussions.

It should not replace customer validation, security review, architecture
assessment, or business-case validation.
"""


def main():

    portfolio_data = load_json(
        PORTFOLIO_PATH
    )

    recommendations_data = load_json(
        RECOMMENDATIONS_PATH
    )

    portfolio = portfolio_data.get(
        "opportunities",
        []
    )

    summary = portfolio_data.get(
        "portfolio_summary",
        {}
    )

    recommendations = {
        item["opportunity_name"]: item
        for item in recommendations_data.get(
            "deployment_recommendations",
            []
        )
    }

    print(
        f"Loaded {len(portfolio)} portfolio opportunities."
    )

    sections = []

    sections.append(
        "# Customer AI Deployment Portfolio"
    )

    sections.append(
        """
> Evidence-backed AI opportunity assessment,
> prioritization, and deployment planning.
"""
    )

    sections.append(
        build_executive_summary(
            portfolio,
            summary
        )
    )

    sections.append(
        build_portfolio_table(
            portfolio
        )
    )

    sections.append(
        build_roadmap(
            portfolio
        )
    )

    sections.append(
        build_evidence_section()
    )

    sections.append(
        "## Detailed Opportunity Assessments"
    )

    for item in portfolio:

        recommendation = recommendations.get(
            item["opportunity_name"],
            {}
        )

        sections.append(
            build_opportunity_section(
                item,
                recommendation
            )
        )

    sections.append(
        build_methodology_section()
    )

    report = "\n".join(
        sections
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        report,
        encoding="utf-8"
    )

    print()
    print(
        "Executive report created."
    )

    print(
        f"Output saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
