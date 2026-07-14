import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
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


def train_logistic_regression(clean_data_path):

    print("🤖 Loading dataset for Logistic Regression...")

    df = pd.read_csv(clean_data_path)

    y = df["dementia_status"]

    X = df.drop(columns=[
        "dementia_status",
        "subject_id",
        "mri_id"
    ])

    # ==========================================================
    # 1. Same train/test split as XGBoost
    # ==========================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(f"\nTraining patients: {len(X_train)}")
    print(f"Testing patients: {len(X_test)}")

    # ==========================================================
    # 2. Build scaling + Logistic Regression pipeline
    # ==========================================================

    model = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "logistic_regression",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ])

    # ==========================================================
    # 3. Train
    # ==========================================================

    print("\n🏋️ Training Logistic Regression...")

    model.fit(X_train, y_train)

    # ==========================================================
    # 4. Predictions
    # ==========================================================

    y_pred = model.predict(X_test)

    y_prob = model.predict_proba(X_test)[:, 1]

    # ==========================================================
    # 5. Metrics
    # ==========================================================

    print("\n✅ --- LOGISTIC REGRESSION PERFORMANCE ---")

    print(f"\nAccuracy : {accuracy_score(y_test, y_pred):.3f}")
    print(f"Precision: {precision_score(y_test, y_pred):.3f}")
    print(f"Recall   : {recall_score(y_test, y_pred):.3f}")
    print(f"F1 Score : {f1_score(y_test, y_pred):.3f}")
    print(f"ROC-AUC  : {roc_auc_score(y_test, y_prob):.3f}")

    print("\nClassification Report")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Nondemented",
                "Demented"
            ]
        )
    )

    # ==========================================================
    # 6. Confusion matrix
    # ==========================================================

    cm = confusion_matrix(y_test, y_pred)

    tn, fp, fn, tp = cm.ravel()

    print("\nConfusion Matrix")
    print(cm)

    print(f"\nTrue Negatives : {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Positives : {tp}")

    # ==========================================================
    # 7. Cross validation
    # ==========================================================

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    cv_auc = cross_val_score(
        model,
        X,
        y,
        cv=cv,
        scoring="roc_auc"
    )

    print("\n5-Fold Cross Validation ROC-AUC")

    print(cv_auc)

    print(f"Mean ROC-AUC: {cv_auc.mean():.3f}")
    print(f"Std Dev     : {cv_auc.std():.3f}")

    # ==========================================================
    # 8. Logistic Regression coefficients
    # ==========================================================

    logistic_model = model.named_steps["logistic_regression"]

    coefficients = pd.DataFrame({
        "Feature": X.columns,
        "Coefficient": logistic_model.coef_[0]
    })

    coefficients["Absolute Coefficient"] = (
        coefficients["Coefficient"].abs()
    )

    coefficients = coefficients.sort_values(
        "Absolute Coefficient",
        ascending=False
    )

    print("\nFeature Coefficients")
    print(coefficients)


if __name__ == "__main__":

    train_logistic_regression(
        "data/clinician_view_data/clinician_mri_clean.csv"
    )