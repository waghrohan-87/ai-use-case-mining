import json
from pathlib import Path

SCORES_PATH = Path("outputs/scored_opportunities.json")
RECOMMENDATIONS_PATH = Path(
    "outputs/deployment_recommendations.json"
)
OUTPUT_PATH = Path(
    "outputs/ai_deployment_portfolio.json"
)


def load_json(path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def text_blob(opportunity, recommendation):
    parts = [
        opportunity.get("opportunity_name", ""),
        opportunity.get("problem_statement", ""),
        opportunity.get("recommended_ai_workflow", ""),
        recommendation.get("deployment_recommendation", ""),
        recommendation.get("recommended_ai_workflow", ""),
        recommendation.get("human_in_the_loop", ""),
    ]

    parts.extend(
        opportunity.get(
            "underlying_workflows",
            []
        )
    )

    parts.extend(
        recommendation.get(
            "required_data_sources",
            []
        )
    )

    parts.extend(
        recommendation.get(
            "likely_integrations",
            []
        )
    )

    return " ".join(parts).lower()


def calculate_complexity(
    opportunity,
    recommendation
):
    text = text_blob(
        opportunity,
        recommendation
    )

    duration = recommendation.get(
        "pilot_duration",
        ""
    ).lower()

    integrations = recommendation.get(
        "likely_integrations",
        []
    )

    data_sources = recommendation.get(
        "required_data_sources",
        []
    )

    dependency_count = (
        len(integrations)
        + len(data_sources)
    )

    score = 0

    # Duration
    if "12 weeks" in duration:
        score += 3
    elif "8-12" in duration:
        score += 3
    elif "8 weeks" in duration:
        score += 2
    elif "6-8" in duration:
        score += 2
    elif "6 weeks" in duration:
        score += 1
    elif "4-6" in duration:
        score += 1

    # System/data dependencies
    if dependency_count >= 7:
        score += 3
    elif dependency_count >= 4:
        score += 2
    elif dependency_count >= 2:
        score += 1

    # Production / real-time workflows
    if any(
        word in text
        for word in [
            "production",
            "real-time",
            "incident",
            "logs",
            "metrics"
        ]
    ):
        score += 2

    # Autonomous or workflow-changing behavior
    if any(
        word in text
        for word in [
            "automatically modifies",
            "automatically publish",
            "autonomous",
            "execute changes"
        ]
    ):
        score += 2

    if score >= 7:
        return "High"

    if score >= 4:
        return "Medium"

    return "Low"


def calculate_risk(
    opportunity,
    recommendation
):
    text = text_blob(
        opportunity,
        recommendation
    )

    name = opportunity.get(
        "opportunity_name",
        ""
    ).lower()

    # High-risk domains
    if (
        "governance" in name
        or "security" in text
        or "compliance" in text
    ):
        return "High"

    # Production incident workflows
    if (
        "incident" in name
        or "production" in text
    ):
        return "High"

    # Code/test recommendations can affect
    # engineering decisions, but are usually
    # manageable with human review.
    if any(
        word in text
        for word in [
            "code review",
            "test generation",
            "legacy code",
            "dependency analysis"
        ]
    ):
        return "Medium"

    # Knowledge/search/summarization workflows
    # are generally lower risk when human review
    # is maintained.
    if any(
        word in text
        for word in [
            "search",
            "documentation",
            "release notes",
            "onboarding",
            "environment setup",
            "requirements"
        ]
    ):
        return "Low"

    return "Medium"


def calculate_readiness(
    opportunity,
    recommendation,
    complexity,
    risk
):
    score = 0

    duration = recommendation.get(
        "pilot_duration",
        ""
    ).lower()

    # Clear pilot scope
    if recommendation.get(
        "pilot_team"
    ):
        score += 25

    # Shorter pilots are easier to start
    if (
        "4-6" in duration
        or "4–6" in duration
    ):
        score += 20
    elif "6 weeks" in duration:
        score += 18
    elif "6-8" in duration:
        score += 15
    elif "8 weeks" in duration:
        score += 12
    else:
        score += 8

    # Measurable success criteria
    metrics = recommendation.get(
        "success_metrics",
        []
    )

    if len(metrics) >= 4:
        score += 20
    elif len(metrics) >= 2:
        score += 15
    elif metrics:
        score += 10

    # Human validation is a positive signal
    human_review = recommendation.get(
        "human_in_the_loop",
        ""
    )

    if human_review:
        score += 20

    # Complexity/risk reduce readiness
    if complexity == "High":
        score -= 10
    elif complexity == "Medium":
        score -= 5

    if risk == "High":
        score -= 10
    elif risk == "Medium":
        score -= 5

    return max(
        0,
        min(
            100,
            score
        )
    )


def calculate_impact(opportunity):
    score = opportunity.get(
        "score",
        0
    )

    if score >= 85:
        return "Very High"

    if score >= 75:
        return "High"

    if score >= 65:
        return "Medium"

    return "Low"


def calculate_adjusted_score(
    opportunity,
    recommendation
):
    base_score = opportunity.get(
        "score",
        0
    )

    complexity = calculate_complexity(
        opportunity,
        recommendation
    )

    risk = calculate_risk(
        opportunity,
        recommendation
    )

    readiness = calculate_readiness(
        opportunity,
        recommendation,
        complexity,
        risk
    )

    complexity_penalty = {
        "Low": 0,
        "Medium": 4,
        "High": 8
    }

    risk_penalty = {
        "Low": 0,
        "Medium": 3,
        "High": 6
    }

    # Readiness contributes up to 10 points.
    readiness_bonus = round(
        readiness / 10
    )

    adjusted_score = (
        base_score
        + readiness_bonus
        - complexity_penalty[complexity]
        - risk_penalty[risk]
    )

    return max(
        0,
        min(
            100,
            adjusted_score
        )
    )


def determine_recommendation(
    adjusted_score,
    complexity,
    risk,
    opportunity,
    recommendation
):
    name = opportunity.get(
        "opportunity_name",
        ""
    ).lower()

    suitability = opportunity.get(
        "ai_suitability",
        "Unknown"
    )

    evidence_count = opportunity.get(
        "evidence_count",
        0
    )

    # Governance/security deserves its own path.
    if (
        "governance" in name
        or "security" in name
    ):
        return "Specialized Review"

    # High-risk workflows need additional
    # validation before a production pilot.
    if risk == "High":
        if (
            adjusted_score >= 85
            and evidence_count >= 2
        ):
            return "Pilot Next"

        return "Validate Further"

    # Strong, evidence-backed, manageable
    # opportunities can start immediately.
    if (
        adjusted_score >= 82
        and complexity == "Low"
        and suitability == "High"
        and evidence_count >= 2
    ):
        return "Pilot Now"

    # Good opportunities with moderate friction.
    if (
        adjusted_score >= 72
        and complexity != "High"
        and suitability in [
            "High",
            "Medium"
        ]
        and evidence_count >= 1
    ):
        return "Pilot Next"

    # Medium-score opportunities can be validated.
    if adjusted_score >= 60:
        return "Validate Further"

    return "Backlog"


def build_portfolio(
    opportunities,
    recommendations
):
    recommendation_map = {
        item["opportunity_name"]: item
        for item in recommendations
    }

    portfolio = []

    for opportunity in opportunities:

        name = opportunity[
            "opportunity_name"
        ]

        recommendation = recommendation_map.get(
            name,
            {}
        )

        complexity = calculate_complexity(
            opportunity,
            recommendation
        )

        risk = calculate_risk(
            opportunity,
            recommendation
        )

        readiness = calculate_readiness(
            opportunity,
            recommendation,
            complexity,
            risk
        )

        impact = calculate_impact(
            opportunity
        )

        adjusted_score = calculate_adjusted_score(
            opportunity,
            recommendation
        )

        decision = determine_recommendation(
            adjusted_score,
            complexity,
            risk,
            opportunity,
            recommendation
        )

        portfolio.append({
            "opportunity_name": name,
            "original_score": opportunity.get(
                "score",
                0
            ),
            "adjusted_score": adjusted_score,
            "priority": opportunity.get(
                "priority",
                "Unknown"
            ),
            "impact": impact,
            "complexity": complexity,
            "deployment_risk": risk,
            "deployment_readiness": readiness,
            "deployment_decision": decision,
            "pilot_team": recommendation.get(
                "pilot_team",
                ""
            ),
            "pilot_duration": recommendation.get(
                "pilot_duration",
                ""
            ),
            "success_metrics": recommendation.get(
                "success_metrics",
                []
            ),
            "deployment_recommendation":
                recommendation.get(
                    "deployment_recommendation",
                    ""
                ),
            "human_in_the_loop":
                recommendation.get(
                    "human_in_the_loop",
                    ""
                ),
            "deployment_blockers":
                recommendation.get(
                    "deployment_blockers",
                    []
                )
        })

    portfolio.sort(
        key=lambda x: x["adjusted_score"],
        reverse=True
    )

    return portfolio


def build_summary(portfolio):

    decisions = [
        "Pilot Now",
        "Pilot Next",
        "Validate Further",
        "Specialized Review",
        "Backlog"
    ]

    summary = {
        "total_opportunities": len(
            portfolio
        )
    }

    for decision in decisions:
        key = (
            decision
            .lower()
            .replace(" ", "_")
        )

        summary[key] = len([
            item
            for item in portfolio
            if item["deployment_decision"]
            == decision
        ])

    return summary


def main():

    scores = load_json(
        SCORES_PATH
    )

    recommendations = load_json(
        RECOMMENDATIONS_PATH
    )

    opportunities = scores.get(
        "opportunities",
        []
    )

    deployment_recommendations = (
        recommendations.get(
            "deployment_recommendations",
            []
        )
    )

    print(
        f"Loaded {len(opportunities)} scored opportunities."
    )

    print(
        f"Loaded "
        f"{len(deployment_recommendations)} "
        f"deployment recommendations."
    )

    portfolio = build_portfolio(
        opportunities,
        deployment_recommendations
    )

    summary = build_summary(
        portfolio
    )

    output = {
        "portfolio_summary": summary,
        "opportunities": portfolio
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            output,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print(
        f"Created portfolio with "
        f"{len(portfolio)} opportunities."
    )

    print(
        f"Output saved to: {OUTPUT_PATH}"
    )

    print()
    print("DEPLOYMENT PORTFOLIO:")

    for item in portfolio:
        print(
            f"{item['adjusted_score']:>3}/100 | "
            f"{item['deployment_decision']:<18} | "
            f"Risk: {item['deployment_risk']:<6} | "
            f"Complexity: {item['complexity']:<6} | "
            f"{item['opportunity_name']}"
        )

    print()
    print("PORTFOLIO SUMMARY:")

    for key, value in summary.items():
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()
