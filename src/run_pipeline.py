import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "gong_transcripts"
)

WORKING_TRANSCRIPTS = DEFAULT_INPUT

STAGES = [
    (
        "Workflow extraction",
        PROJECT_ROOT / "src" / "extract_workflows.py"
    ),
    (
        "Semantic clustering",
        PROJECT_ROOT / "src" / "cluster_workflows.py"
    ),
    (
        "AI opportunity synthesis",
        PROJECT_ROOT / "src" / "synthesize_opportunities.py"
    ),
    (
        "Opportunity scoring",
        PROJECT_ROOT / "src" / "score_opportunities.py"
    ),
    (
        "Deployment recommendations",
        PROJECT_ROOT / "src" / "recommend_deployment.py"
    ),
    (
        "Deployment portfolio",
        PROJECT_ROOT / "src" / "build_portfolio.py"
    ),
    (
        "Executive report",
        PROJECT_ROOT / "src" / "build_executive_report.py"
    ),
]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete AI use-case mining pipeline."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help=(
            "Directory containing customer transcript "
            "text files."
        )
    )

    return parser.parse_args()


def validate_input(input_dir):
    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}"
        )

    if not input_dir.is_dir():
        raise NotADirectoryError(
            f"Input path is not a directory: {input_dir}"
        )

    transcripts = list(
        input_dir.glob("*.txt")
    )

    if not transcripts:
        raise FileNotFoundError(
            f"No .txt transcript files found in: {input_dir}"
        )

    return transcripts


def prepare_transcripts(
    transcripts,
    input_dir
):
    print()
    print("Preparing transcript input...")

    # If the user supplied the existing default
    # transcript directory, do not copy anything.
    if input_dir == WORKING_TRANSCRIPTS:
        print(
            "Using existing transcript directory directly."
        )

        return

    WORKING_TRANSCRIPTS.mkdir(
        parents=True,
        exist_ok=True
    )

    # Clear only the working copies.
    # The customer's source directory is never modified.
    for existing in WORKING_TRANSCRIPTS.glob(
        "*.txt"
    ):
        existing.unlink()

    copied = 0

    for transcript in transcripts:

        if not transcript.exists():
            raise FileNotFoundError(
                f"Transcript disappeared before copying: "
                f"{transcript}"
            )

        destination = (
            WORKING_TRANSCRIPTS
            / transcript.name
        )

        shutil.copy2(
            transcript,
            destination
        )

        copied += 1

    print(
        f"Copied {copied} transcript(s) "
        f"into the pipeline working directory."
    )


def run_stage(
    stage_number,
    total_stages,
    name,
    script
):
    print()
    print("=" * 70)
    print(
        f"STAGE {stage_number}/{total_stages}: {name}"
    )
    print("=" * 70)

    command = [
        sys.executable,
        str(script)
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        print()
        print(
            f"ERROR: Stage failed: {name}"
        )

        print(
            f"Script: {script}"
        )

        raise RuntimeError(
            f"Pipeline stopped at stage "
            f"{stage_number}: {name}"
        )

    print()
    print(
        f"✓ Completed: {name}"
    )


def print_final_summary():
    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print()
    print("Generated outputs:")

    outputs = [
        "outputs/workflow_observations.json",
        "outputs/workflow_clusters.json",
        "outputs/ai_opportunities.json",
        "outputs/scored_opportunities.json",
        "outputs/deployment_recommendations.json",
        "outputs/ai_deployment_portfolio.json",
        "outputs/executive_ai_report.md",
    ]

    for output in outputs:

        path = PROJECT_ROOT / output

        if path.exists():
            print(
                f"✓ {output}"
            )
        else:
            print(
                f"⚠ Missing: {output}"
            )

    print()
    print(
        "The customer AI deployment portfolio "
        "and executive report are ready."
    )


def main():

    args = parse_args()

    input_dir = Path(
        args.input
    ).expanduser().resolve()

    print("=" * 70)
    print("AI USE-CASE MINING ENGINE")
    print("=" * 70)

    print()
    print(
        f"Input directory: {input_dir}"
    )

    transcripts = validate_input(
        input_dir
    )

    print(
        f"Found {len(transcripts)} transcript(s)."
    )

    prepare_transcripts(
        transcripts,
        input_dir
    )

    total_stages = len(STAGES)

    for index, (
        name,
        script
    ) in enumerate(
        STAGES,
        start=1
    ):
        run_stage(
            index,
            total_stages,
            name,
            script
        )

    print_final_summary()


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        print()
        print(
            "Pipeline interrupted by user."
        )

        sys.exit(130)

    except Exception as exc:

        print()
        print(
            f"Pipeline failed: {exc}"
        )

        sys.exit(1)
