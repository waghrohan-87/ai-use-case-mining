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
2. Do not assume every pain point should be solved with AI.
3. Preserve uncertainty.
4. If a field is unknown, use null.
5. ai_suitability must be exactly one of:
   "High", "Medium", "Low", or "Unknown".
6. confidence must be a number between 0 and 1.
7. estimated_effort_hours must be a number or null.
8. Evidence must be directly supported by the conversation.
9. Do not invent metrics or facts.
10. Return ONLY valid JSON. Do not use Markdown code fences.

Return exactly this structure:

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
