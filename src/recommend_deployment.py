import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

INPUT_PATH = Path("outputs/scored_opportunities.json")
OUTPUT_PATH = Path("outputs/deployment_recommendations.json")


def load_opportunities():
    data = json.loads(
        INPUT_PATH.read_text(
            encoding="utf-8"
        )
    )

    return data.get(
        "opportunities",
        []
    )


def generate_recommendation(opportunity):

    prompt = f"""
You are an expert Enterprise AI Deployment Manager.

Create a practical deployment recommendation for the following
AI opportunity.

Your recommendation must be grounded ONLY in the evidence provided.

Do not invent customer facts.

The goal is to determine how this opportunity could be safely piloted,
measured, and eventually expanded.

Consider:

- pilot team
- target personas
- required data sources
- likely integrations
- recommended AI workflow
- human validation
- security considerations
- adoption strategy
- pilot duration
- success metrics
- expansion criteria
- deployment blockers

A high score does NOT automatically mean immediate deployment.

Prefer a focused pilot before broad rollout.

AI-generated outputs that could affect engineering decisions should have
appropriate human validation.

OPPORTUNITY:

{json.dumps(opportunity, indent=2)}
"""

    schema = {
        "type": "object",
        "properties": {
            "opportunity_name": {
                "type": "string"
            },
            "priority_score": {
                "type": "number"
            },
            "deployment_recommendation": {
                "type": "string"
            },
            "pilot_team": {
                "type": "string"
            },
            "target_personas": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "required_data_sources": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "likely_integrations": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "recommended_ai_workflow": {
                "type": "string"
            },
            "human_in_the_loop": {
                "type": "string"
            },
            "security_considerations": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "adoption_strategy": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "pilot_duration": {
                "type": "string"
            },
            "success_metrics": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "expansion_criteria": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "deployment_blockers": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": [
            "opportunity_name",
            "priority_score",
            "deployment_recommendation",
            "pilot_team",
            "target_personas",
            "required_data_sources",
            "likely_integrations",
            "recommended_ai_workflow",
            "human_in_the_loop",
            "security_considerations",
            "adoption_strategy",
            "pilot_duration",
            "success_metrics",
            "expansion_criteria",
            "deployment_blockers"
        ],
        "additionalProperties": False
    }

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2500,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": schema
            }
        }
    )

    text = response.content[0].text

    return json.loads(text)


def main():

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError(
            "ANTHROPIC_API_KEY is not configured."
        )

    opportunities = load_opportunities()

    print(
        f"Found {len(opportunities)} opportunities."
    )

    recommendations = []

    for index, opportunity in enumerate(
        opportunities,
        start=1
    ):

        name = opportunity.get(
            "opportunity_name",
            "Unknown opportunity"
        )

        print(
            f"[{index}/{len(opportunities)}] "
            f"Generating recommendation: {name}"
        )

        recommendation = generate_recommendation(
            opportunity
        )

        recommendations.append(
            recommendation
        )

    output = {
        "deployment_recommendations":
            recommendations
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
        f"Created {len(recommendations)} deployment recommendations."
    )

    print(
        f"Output saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
