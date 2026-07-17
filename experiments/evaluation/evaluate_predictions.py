"""Evaluate saved BrainGuard AI prediction results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from experiments.evaluation.metrics import evaluate_classifier
from experiments.evaluation.plots import save_confusion_matrix


def evaluate_prediction_file(
    prediction_path: str,
    output_directory: str,
) -> dict:
    """
    Evaluate a CSV containing at least:
        y_true
        y_pred

    Optional binary probability column:
        probability
    """
    prediction_file = Path(prediction_path)

    if not prediction_file.exists():
        raise FileNotFoundError(
            f"Prediction file was not found: {prediction_file}"
        )

    data = pd.read_csv(prediction_file)

    required_columns = {"y_true", "y_pred"}
    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            "Prediction file is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    probability = (
        data["probability"].to_numpy()
        if "probability" in data.columns
        else None
    )

    results = evaluate_classifier(
        y_true=data["y_true"],
        y_pred=data["y_pred"],
        y_probability=probability,
    )

    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(
        output_path / "metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(results, file, indent=2)

    save_confusion_matrix(
        y_true=data["y_true"],
        y_pred=data["y_pred"],
        output_path=output_path / "confusion_matrix.png",
    )

    data.to_csv(output_path / "predictions.csv", index=False)

    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()

    results = evaluate_prediction_file(
        prediction_path=arguments.predictions,
        output_directory=arguments.output,
    )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()