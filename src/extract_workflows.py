import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

TRANSCRIPTS_DIR = Path("data/gong_transcripts")
OUTPUT_PATH = Path("outputs/workflow_observations.json")


def extract_workflows(transcript: str, filename: str) -> dict:
    prompt = f"""
You are an expert Enterprise AI Deployment Manager and Customer Success
strategist.

Analyze the customer conversation below.

Your job is NOT to recommend an AI product yet.

Identify the real human workflows, repetitive tasks, pain points, and
potential opportunities for AI assistance that are explicitly supported
by the conversation.

Be conservative. Do not invent information.

For every meaningful workflow, extract:

- workflow
- team
- persona
- pain_point
- current_process
- frequency
- estimated_effort_hours
- ai_suitability
- evidence
- confidence

Also identify important organizational context:

- current_ai_adoption
- adoption_stage
- decision_maker_priority
- pilot_readiness
- key_concerns

Rules:
1. Separate actual workflows from general opinions.

2. Identify the underlying repeatable human activity, not the person,
   example, tool, project, or individual incident.

3. Name each workflow using a concise, reusable activity description.
   Prefer a verb + object structure such as:
   - Writing unit and regression tests
   - Maintaining existing test suites
   - Reviewing pull requests
   - Finding technical documentation
   - Refining engineering requirements
   - Investigating production incidents

4. Do NOT include individual names, seniority, team member names,
   specific products, specific projects, or incidental examples in the
   workflow name unless they materially define the workflow.

5. Do not create duplicate workflows when different people, roles, or
   teams perform the same underlying activity.

   However, keep genuinely different activities separate even when they
   occur within the same broader business process.

6. When in doubt, preserve a distinct workflow if the human task,
   objective, or output is materially different.

7. Use the same workflow concept consistently across transcripts.
   Prefer common enterprise workflow terminology over creative or
   conversational wording.

8. Do not infer a workflow merely because it would logically exist.
   It must be explicitly supported by the conversation.

9. Be conservative. Do not invent information.

10. Preserve uncertainty.

11. If a field is unknown, use null.

12. ai_suitability must be exactly one of:
    "High", "Medium", "Low", or "Unknown".

13. confidence must be a number between 0 and 1.

14. estimated_effort_hours must be a number or null.

15. Evidence must be directly supported by the conversation.

16. Do not invent metrics, frequency, effort, or facts.

17. Return ONLY valid JSON. Do not use Markdown code fences.


Return exactly this structure:

WORKFLOW NAMING STANDARD:

Every workflow name must represent the reusable human activity that
could occur repeatedly across an organization.

Use concise names of approximately 3-8 words.

Good examples:
- Writing unit and regression tests
- Maintaining existing test suites
- Reviewing pull requests
- Finding technical documentation
- Updating technical documentation
- Refining engineering requirements
- Investigating production incidents
- Preparing release notes
- Setting up developer environments

Avoid names such as:
- Senior engineer reviewing junior developer tests
- Alex spending two hours writing tests
- Finding documentation in Confluence
- Incident with payment service X
- Developer having trouble with their laptop

The workflow name should remain useful if the customer, team, tool,
project, and individual names were removed from the transcript.

{{
  "source_file": "{filename}",
  "customer": "string",
  "workflows": [
    {{
      "workflow": "string",
      "team": "string or null",
      "persona": "string or null",
      "pain_point": "string",
      "current_process": "string",
      "frequency": "string or null",
      "estimated_effort_hours": "number or null",
      "ai_suitability": "High, Medium, Low, or Unknown",
      "evidence": "string",
      "confidence": 0.0
    }}
  ],
  "organizational_context": {{
    "current_ai_adoption": "string or null",
    "adoption_stage": "string or null",
    "decision_maker_priority": "string or null",
    "pilot_readiness": "string or null",
    "key_concerns": []
  }}
}}

CUSTOMER CONVERSATION:

{transcript}
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    text = response.content[0].text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    return json.loads(text)


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError(
            "ANTHROPIC_API_KEY is not configured. "
            "Check your .env file."
        )

    transcript_files = sorted(
        TRANSCRIPTS_DIR.glob("*.txt")
    )

    if not transcript_files:
        raise FileNotFoundError(
            f"No transcript files found in {TRANSCRIPTS_DIR}"
        )

    all_results = []

    print(f"Found {len(transcript_files)} transcript(s).")

    for index, transcript_path in enumerate(transcript_files, start=1):
        print(
            f"[{index}/{len(transcript_files)}] "
            f"Processing {transcript_path.name}..."
        )

        transcript = transcript_path.read_text(
            encoding="utf-8"
        )

        result = extract_workflows(
            transcript,
            transcript_path.name
        )

        all_results.append(result)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        json.dumps(all_results, indent=2),
        encoding="utf-8"
    )

    print()
    print(f"Completed: {len(all_results)} transcripts")
    print(f"Output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
