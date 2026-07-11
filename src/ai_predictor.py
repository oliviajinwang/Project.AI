import json

import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
import os
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score, StratifiedGroupKFold
from sklearn.calibration import CalibratedClassifierCV

def train_pure_clinical_model(clean_data_path):
    print("🤖 Loading pre-cleaned numeric dataset...")
    df = pd.read_csv(clean_data_path)
    print(df.columns.tolist())
    
    # 1. Isolate target and predictive features
    # Assumes 'dementia_status' contains your numeric targets (0, 1, 2)

    y = df['dementia_status']
    groups = df['subject_id']

    X = df.drop(columns=[
        'dementia_status',
        'subject_id',
        'mri_id'
    ])


    # 2. Group-aware Train/Test Split. OASIS-2 has 373 sessions from only
    # 150 subjects with repeat visits -- a random/stratified row split lets
    # the same subject land in both train and test, so the model partly
    # memorizes people instead of learning disease signal. GroupShuffleSplit
    # keeps every visit for a given Subject ID entirely on one side.
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    print(f"📊 Training Matrix Size: {X_train.shape[0]} patients")
    print(f"📊 Testing Matrix Size: {X_test.shape[0]} patients")
    
    # 3. Configure and Train the XGBoost Multi-Class Predictor
    print("🏋️ Fitting XGBoost Multi-Class Framework...")

    base_model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        n_estimators=200,
        learning_rate=0.03,
        max_depth=3,
        subsample=0.8,
        colsample_bytree=0.7,
        reg_alpha=0.1,          # Added regularization
        reg_lambda=1.0,         # Added regularization
        random_state=42
    )

    base_model.fit(X_train, y_train)

    print("\nColumns in X_train:")
    print(X_train.columns.tolist())

    print("\nDtypes in X_train:")
    print(X_train.dtypes)

    print("\nAny object columns?")
    print(X_train.select_dtypes(include=["object", "string"]).columns.tolist())

    model = CalibratedClassifierCV(
        base_model,
        method="isotonic",
        cv=5
    )

    model.fit(X_train, y_train)

    # 4. Generate Predictions & Validate Target Metrics

    importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": base_model.feature_importances_
    }).sort_values(
        by="Importance",
        ascending=False
    )

    print("\nFeature Importance")
    print(importance)

    # importance = importance.sort_values(
    #     "Importance",
    #     ascending=False
    # )

    # print("\nFeature Importance")
    # print(importance)
    
    # Cross-Validation for Model Robustness (group-aware so a subject's
    # repeat visits never split across the train/validation side of a fold)
    scores = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="accuracy"
    )
    print("\n5-Fold Cross Validation")
    print(scores)

    print(
        f"Mean Accuracy: {scores.mean():.3f}"
    )
    print(
        f"Std Dev: {scores.std():.3f}"
    )

    # Three-way classification (Nondemented / Demented / Converted) has no
    # single "positive class" decision threshold to tune the way the old
    # binary model did (that F2/precision-recall-curve approach only makes
    # sense for one positive class vs. the rest). Predict whichever class
    # has the highest calibrated probability instead (argmax) -- the
    # standard approach for multi-class problems.
    y_prob = model.predict_proba(X_test)
    y_pred = np.argmax(y_prob, axis=1)

    print("\nFirst 10 probability predictions:")

    for i in range(10):
        print(
            f"True={y_test.iloc[i]} "
            f"Prob={y_prob[i][1]:.3f}"
        )

    print("\n✅ --- TESTING PERFORMANCE METRICS ---")
    
    print("Before argmax:")
    print("Shape:", y_pred.shape)
    print("First prediction:", y_pred[0])

    #y_pred = np.argmax(y_pred, axis=1)

    print("\nAfter argmax:")
    print("Shape:", y_pred.shape)
    print("First 10 predictions:", y_pred[:10])

    print("\ny_test shape:", y_test.shape)
    print("First 10 true labels:", y_test[:10].to_numpy())

    print(f"Global Model Accuracy: {round(accuracy_score(y_test, y_pred) * 100, 2)}%")
    print("\nClassification Matrix Breakdown:")

    print("Unique true labels:", np.unique(y_test))
    print("Unique predicted labels:", np.unique(y_pred))
    print(df["dementia_status"].value_counts())
    class_names = ['Nondemented (0)', 'Demented (1)', 'Converted (2)']
    print(classification_report(y_test, y_pred, labels=[0, 1, 2], target_names=class_names, zero_division=0))

    # Confusion Matrix for further insight into model performance. A 3x3
    # matrix has no single tn/fp/fn/tp breakdown the way a binary one does
    # -- the per-class precision/recall above already covers that.
    print("\nConfusion Matrix (rows = true class, columns = predicted class)")
    print("Order: Nondemented (0), Demented (1), Converted (2)")
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
    print(cm)

    # Metrics for model evaluation. Macro-averaged so the rare "Converted"
    # class (37 of 373 rows) isn't washed out by the two larger classes.
    print("\nKey Metrics (macro-averaged across all 3 classes)")
    print(f"Accuracy : {accuracy_score(y_test, y_pred):.3f}")
    print(f"Precision: {precision_score(y_test, y_pred, average='macro', zero_division=0):.3f}")
    print(f"Recall   : {recall_score(y_test, y_pred, average='macro', zero_division=0):.3f}")
    print(f"F1 Score : {f1_score(y_test, y_pred, average='macro', zero_division=0):.3f}")

    # One-vs-rest ROC-AUC, macro-averaged across the 3 classes.
    auc = roc_auc_score(y_test, y_prob, multi_class="ovr", average="macro", labels=[0, 1, 2])
    print(f"\nMacro ROC-AUC (one-vs-rest): {auc:.3f}")

    # 5. Build Tree-Based SHAP Structure
    print("🔍 Pre-computing SHAP Explainer objects...")
    explainer = shap.TreeExplainer(base_model)

    # 6. Export Binary Assets to the Team Folder
    os.makedirs("models", exist_ok=True)
    print("💾 Dumping pickled objects to /models directory...")

    joblib.dump(model, "models/clinician_model.pkl")
    joblib.dump(explainer, "models/clinician_shap_explainer.pkl")

    # Export a test schema reference row for Person 3's pipeline matching
    X_test.head(1).to_csv("models/clinical_sample_input.csv", index=False)

    macro_f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    with open("models/clinical_metrics.json", "w") as f:
        json.dump({
            "accuracy": round(accuracy_score(y_test, y_pred) * 100, 1),
            "roc_auc": round(auc * 100, 1),
            "macro_f1": round(macro_f1 * 100, 1),
        }, f)

    print("🎉 Production assets ready for UI population!")

if __name__ == "__main__":
    # Point this path straight to your clean output from Week 1!
    train_pure_clinical_model("data/clinician_view_data/clinician_mri_clean.csv")