import pandas as pd
import numpy as np

from sklearn.model_selection import (
    StratifiedGroupKFold,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)


RANDOM_STATE = 42


def train_logistic_regression(clean_data_path):
    print("🤖 Loading dataset for Logistic Regression...")

    df = pd.read_csv(clean_data_path)

    # ==========================================================
    # 1. Prepare features, binary target, and subject groups
    # ==========================================================

    # 0 = Nondemented
    # 1 = Demented or Converted
    y = (
        df["dementia_status"]
        .replace({2: 1})
        .astype(int)
    )

    groups = df["subject_id"]

    X = df.drop(
        columns=[
            "dementia_status",
            "subject_id",
            "mri_id",
        ]
    )

    print("\nBinary target distribution:")
    print(y.value_counts().sort_index())

    # ==========================================================
    # 2. Subject-separated, approximately 80/20 holdout split
    # ==========================================================

    holdout_splitter = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    train_idx, test_idx = next(
        holdout_splitter.split(
            X,
            y,
            groups=groups,
        )
    )

    X_train = X.iloc[train_idx].copy()
    X_test = X.iloc[test_idx].copy()

    y_train = y.iloc[train_idx].copy()
    y_test = y.iloc[test_idx].copy()

    groups_train = groups.iloc[train_idx].copy()
    groups_test = groups.iloc[test_idx].copy()

    overlap = set(groups_train) & set(groups_test)

    if overlap:
        raise RuntimeError(
            "Subject leakage detected between training and testing."
        )

    print("\n✅ No subject overlap between training and testing.")

    print(f"\nTraining visits : {len(X_train)}")
    print(f"Testing visits  : {len(X_test)}")
    print(f"Training subjects: {groups_train.nunique()}")
    print(f"Testing subjects : {groups_test.nunique()}")

    print("\nTraining class proportions:")
    print(y_train.value_counts(normalize=True).sort_index())

    print("\nTesting class proportions:")
    print(y_test.value_counts(normalize=True).sort_index())

    # ==========================================================
    # 3. Build scaling + Logistic Regression pipeline
    # ==========================================================

    model = Pipeline([
        (
            "scaler",
            StandardScaler(),
        ),
        (
            "logistic_regression",
            LogisticRegression(
                max_iter=2000,
                random_state=RANDOM_STATE,
            ),
        ),
    ])

    # ==========================================================
    # 4. Train
    # ==========================================================

    print("\n🏋️ Training Logistic Regression...")

    model.fit(
        X_train,
        y_train,
    )

    # ==========================================================
    # 5. Predictions
    # ==========================================================

    y_pred = model.predict(X_test)

    y_prob = model.predict_proba(X_test)[:, 1]
    print("\n🧪 Logistic Regression Threshold Diagnostics")

    threshold_rows = []

    for threshold in np.arange(0.30, 0.71, 0.05):
        threshold_pred = (
            y_prob >= threshold
        ).astype(int)

        threshold_rows.append({
            "threshold": threshold,
            "accuracy": accuracy_score(
                y_test,
                threshold_pred
            ),
            "precision": precision_score(
                y_test,
                threshold_pred,
                zero_division=0
            ),
            "recall": recall_score(
                y_test,
                threshold_pred,
                zero_division=0
            ),
            "f1": f1_score(
                y_test,
                threshold_pred,
                zero_division=0
            ),
        })

    threshold_results = pd.DataFrame(threshold_rows)

    print(
        threshold_results
        .round(3)
        .to_string(index=False)
    )

    # ==========================================================
    # 6. Holdout metrics
    # ==========================================================

    accuracy = accuracy_score(
        y_test,
        y_pred,
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        y_prob,
    )

    print("\n✅ --- LOGISTIC REGRESSION PERFORMANCE ---")

    print(f"Accuracy : {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall   : {recall:.3f}")
    print(f"F1 Score : {f1:.3f}")
    print(f"ROC-AUC  : {roc_auc:.3f}")

    print("\nClassification Report")

    print(
        classification_report(
            y_test,
            y_pred,
            labels=[0, 1],
            target_names=[
                "Nondemented (0)",
                "Demented / Converted (1)",
            ],
            zero_division=0,
        )
    )

    # ==========================================================
    # 7. Confusion matrix
    # ==========================================================

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1],
    )

    tn, fp, fn, tp = cm.ravel()

    print("\nConfusion Matrix")
    print(cm)

    print(f"\nTrue Negatives : {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Positives : {tp}")

    # ==========================================================
    # 8. Group-aware cross-validation
    # ==========================================================

    cv = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    cv_accuracy = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=cv,
        scoring="accuracy",
    )

    cv_precision = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=cv,
        scoring="precision",
    )

    cv_recall = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=cv,
        scoring="recall",
    )

    cv_f1 = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=cv,
        scoring="f1",
    )

    cv_auc = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=cv,
        scoring="roc_auc",
    )

    print("\n🔁 --- 5-FOLD GROUP-AWARE CROSS-VALIDATION ---")

    print(
        f"Accuracy : "
        f"{cv_accuracy.mean():.3f} "
        f"± {cv_accuracy.std():.3f}"
    )

    print(
        f"Precision: "
        f"{cv_precision.mean():.3f} "
        f"± {cv_precision.std():.3f}"
    )

    print(
        f"Recall   : "
        f"{cv_recall.mean():.3f} "
        f"± {cv_recall.std():.3f}"
    )

    print(
        f"F1 Score : "
        f"{cv_f1.mean():.3f} "
        f"± {cv_f1.std():.3f}"
    )

    print(
        f"ROC-AUC  : "
        f"{cv_auc.mean():.3f} "
        f"± {cv_auc.std():.3f}"
    )

    # ==========================================================
    # 9. Logistic Regression coefficients
    # ==========================================================

    logistic_model = model.named_steps[
        "logistic_regression"
    ]

    coefficients = pd.DataFrame({
        "Feature": X.columns,
        "Coefficient": logistic_model.coef_[0],
    })

    coefficients["Absolute Coefficient"] = (
        coefficients["Coefficient"].abs()
    )

    coefficients = coefficients.sort_values(
        "Absolute Coefficient",
        ascending=False,
    )

    print("\nFeature Coefficients")
    print(coefficients.to_string(index=False))


if __name__ == "__main__":
    train_logistic_regression(
        "data/clinician_view_data/clinician_mri_clean.csv"
    )