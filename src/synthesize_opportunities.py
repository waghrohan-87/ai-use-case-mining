import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

INPUT_PATH = Path("outputs/workflow_clusters.json")
OUTPUT_PATH = Path("outputs/ai_opportunities.json")


def load_clusters():
    return json.loads(
        INPUT_PATH.read_text(encoding="utf-8")
    )


def synthesize_opportunities(clusters):

    prompt = f"""
You are an expert Enterprise AI Deployment Manager.

Analyze the candidate workflow clusters below.

Your goal is to consolidate related workflow clusters into canonical,
deployable AI opportunities.

Do not simply rename clusters.

Combine workflows when they represent the same underlying business problem,
user need, or AI-enabled workflow.

Keep workflows separate when they require materially different users,
systems, deployment approaches, or success metrics.

Do not invent customer facts.

Every opportunity must be supported by evidence from the input.

Security, governance, and adoption blockers should be represented as
constraints rather than incorrectly classified as productivity opportunities.

For each opportunity identify:

- opportunity name
- problem statement
- underlying workflows
- teams
- personas
- evidence count
- AI suitability
- why AI is relevant
- recommended AI workflow
- potential pilot team
- likely systems involved
- adoption considerations
- key risks
- supporting evidence
- confidence

AI suitability must be High, Medium, Low, or Unknown.

Confidence must be between 0 and 1.

CANDIDATE WORKFLOW CLUSTERS:

{json.dumps(clusters, indent=2)}
"""

    schema = {
        "type": "object",
        "properties": {
            "opportunities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "opportunity_name": {
                            "type": "string"
                        },
                        "problem_statement": {
                            "type": "string"
                        },
                        "underlying_workflows": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "teams": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "personas": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "evidence_count": {
                            "type": "integer"
                        },
                        "ai_suitability": {
                            "type": "string",
                            "enum": [
                                "High",
                                "Medium",
                                "Low",
                                "Unknown"
                            ]
                        },
                        "why_ai_is_relevant": {
                            "type": "string"
                        },
                        "recommended_ai_workflow": {
                            "type": "string"
                        },
                        "potential_pilot_team": {
                            "type": "string"
                        },
                        "likely_systems_involved": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "adoption_considerations": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "key_risks": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "supporting_evidence": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "confidence": {
                            "type": "number"
                        }
                    },
                    "required": [
                        "opportunity_name",
                        "problem_statement",
                        "underlying_workflows",
                        "teams",
                        "personas",
                        "evidence_count",
                        "ai_suitability",
                        "why_ai_is_relevant",
                        "recommended_ai_workflow",
                        "potential_pilot_team",
                        "likely_systems_involved",
                        "adoption_considerations",
                        "key_risks",
                        "supporting_evidence",
                        "confidence"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "opportunities"
        ],
        "additionalProperties": False
    }

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=6000,
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

    clusters = load_clusters()

    print(
        f"Loaded {len(clusters)} candidate workflow clusters."
    )

    print(
        "Calling Claude for opportunity synthesis..."
    )

    opportunities = synthesize_opportunities(clusters)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        json.dumps(opportunities, indent=2),
        encoding="utf-8"
    )

    count = len(
        opportunities["opportunities"]
    )

    print()
    print(
        f"Created {count} canonical AI opportunities."
    )

    print(
        f"Output saved to: {OUTPUT_PATH}"
    )

    print()
    print("AI OPPORTUNITIES:")

    for opportunity in opportunities["opportunities"]:
        print(
            f"- {opportunity['opportunity_name']}"
            f" | {opportunity['ai_suitability']}"
        )


if __name__ == "__main__":
    main()
