import json
from pathlib import Path

INPUT_PATH = Path("outputs/ai_opportunities.json")
OUTPUT_PATH = Path("outputs/scored_opportunities.json")


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def calculate_score(opportunity):
    evidence_count = opportunity.get("evidence_count", 0)
    ai_suitability = opportunity.get(
        "ai_suitability",
        "Unknown"
    )
    confidence = opportunity.get(
        "confidence",
        0
    )

    # 1. Evidence strength: 0-20
    evidence_score = clamp(
        evidence_count * 4,
        0,
        20
    )

    # 2. AI suitability: 0-25
    suitability_scores = {
        "High": 25,
        "Medium": 17,
        "Low": 8,
        "Unknown": 0
    }

    ai_score = suitability_scores.get(
        ai_suitability,
        0
    )

    # 3. Confidence: 0-20
    confidence_score = clamp(
        confidence * 20,
        0,
        20
    )

    # 4. Workflow clarity: 0-15
    workflow_count = len(
        opportunity.get(
            "underlying_workflows",
            []
        )
    )

    workflow_score = clamp(
        workflow_count * 3,
        0,
        15
    )

    # 5. Deployment readiness: 0-20
    pilot_team = opportunity.get(
        "potential_pilot_team",
        ""
    )

    systems = opportunity.get(
        "likely_systems_involved",
        []
    )

    readiness_score = 0

    if pilot_team:
        readiness_score += 10

    if systems:
        readiness_score += 5

    if opportunity.get(
        "recommended_ai_workflow"
    ):
        readiness_score += 5

    readiness_score = clamp(
        readiness_score,
        0,
        20
    )

    total_score = round(
        evidence_score
        + ai_score
        + confidence_score
        + workflow_score
        + readiness_score
    )

    if total_score >= 80:
        priority = "P1 - High Priority"
    elif total_score >= 60:
        priority = "P2 - Medium Priority"
    elif total_score >= 40:
        priority = "P3 - Explore"
    else:
        priority = "P4 - Low Priority"

    return {
        "total_score": total_score,
        "priority": priority,
        "score_breakdown": {
            "evidence_strength": round(
                evidence_score,
                1
            ),
            "ai_suitability": ai_score,
            "confidence": round(
                confidence_score,
                1
            ),
            "workflow_clarity": workflow_score,
            "deployment_readiness": readiness_score
        }
    }


def main():

    data = json.loads(
        INPUT_PATH.read_text(
            encoding="utf-8"
        )
    )

    opportunities = data.get(
        "opportunities",
        []
    )

    scored_opportunities = []

    for opportunity in opportunities:

        scoring = calculate_score(
            opportunity
        )

        scored_opportunity = {
            **opportunity,
            "score": scoring["total_score"],
            "priority": scoring["priority"],
            "score_breakdown": scoring[
                "score_breakdown"
            ]
        }

        scored_opportunities.append(
            scored_opportunity
        )

    scored_opportunities.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    output = {
        "opportunities": scored_opportunities
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

    print(
        f"Scored {len(scored_opportunities)} opportunities."
    )

    print(
        f"Output saved to: {OUTPUT_PATH}"
    )

    print()
    print("OPPORTUNITY PRIORITY:")

    for opportunity in scored_opportunities:

        print(
            f"{opportunity['score']:>3}/100 | "
            f"{opportunity['priority']:<20} | "
            f"{opportunity['opportunity_name']}"
        )


if __name__ == "__main__":
    main()
