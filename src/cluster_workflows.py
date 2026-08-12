import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

INPUT_PATH = Path("outputs/workflow_observations.json")
OUTPUT_PATH = Path("outputs/workflow_clusters.json")


def load_workflows():
    data = json.loads(
        INPUT_PATH.read_text(encoding="utf-8")
    )

    workflows = []

    for transcript in data:
        for workflow in transcript["workflows"]:
            workflows.append({
                "source_file": transcript["source_file"],
                **workflow
            })

    return workflows


def build_workflow_text(workflow):
    return (
        f"{workflow['workflow']}. "
        f"Pain point: {workflow['pain_point']}. "
        f"Current process: {workflow['current_process']}."
    )


def main():
    workflows = load_workflows()

    print(f"Found {len(workflows)} workflow observations.")

    texts = [
        build_workflow_text(workflow)
        for workflow in workflows
    ]

    print("Loading embedding model...")

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    similarity_matrix = cosine_similarity(embeddings)

    distance_matrix = 1 - similarity_matrix

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=0.32,
        metric="precomputed",
        linkage="average"
    )

    labels = clustering.fit_predict(
        distance_matrix
    )

    clusters = {}

    for index, label in enumerate(labels):
        clusters.setdefault(
            int(label),
            []
        ).append(workflows[index])

    output = []

    for cluster_id, members in clusters.items():
        output.append({
            "cluster_id": cluster_id,
            "observation_count": len(members),
            "workflows": members
        })

    output.sort(
        key=lambda x: x["observation_count"],
        reverse=True
    )

    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8"
    )

    print()
    print(f"Created {len(output)} workflow clusters.")
    print(f"Output saved to: {OUTPUT_PATH}")

    print()
    print("CLUSTERS:")

    for cluster in output:
        print(
            f"\nCluster {cluster['cluster_id']} "
            f"({cluster['observation_count']} observations)"
        )

        for workflow in cluster["workflows"]:
            print(
                f"  - {workflow['workflow']}"
            )


if __name__ == "__main__":
    main()
