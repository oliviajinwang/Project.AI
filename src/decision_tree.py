import pandas as pd

from sklearn.model_selection import (
    StratifiedGroupKFold,
    cross_val_score,
)
from sklearn.tree import DecisionTreeClassifier
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


def train_decision_tree(clean_data_path):
    print("🌳 Loading dataset for Decision Tree...")

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

    # One of five folds becomes the test set.
    # All visits from the same subject stay together.
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
    # 3. Select tree depth using training subjects only
    # ==========================================================

    training_cv = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    depth_results = []

    print("\n🌳 Testing Decision Tree Depths")

    for depth in range(2, 8):
        candidate_model = DecisionTreeClassifier(
            max_depth=depth,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
        )

        auc_scores = cross_val_score(
            candidate_model,
            X_train,
            y_train,
            groups=groups_train,
            cv=training_cv,
            scoring="roc_auc",
        )

        accuracy_scores = cross_val_score(
            candidate_model,
            X_train,
            y_train,
            groups=groups_train,
            cv=training_cv,
            scoring="accuracy",
        )

        depth_results.append({
            "depth": depth,
            "mean_roc_auc": auc_scores.mean(),
            "std_roc_auc": auc_scores.std(),
            "mean_accuracy": accuracy_scores.mean(),
            "std_accuracy": accuracy_scores.std(),
        })

        print(
            f"Depth {depth}: "
            f"ROC-AUC={auc_scores.mean():.3f} "
            f"± {auc_scores.std():.3f}, "
            f"Accuracy={accuracy_scores.mean():.3f} "
            f"± {accuracy_scores.std():.3f}"
        )

    depth_df = pd.DataFrame(depth_results)

    depth_df = depth_df.dropna(
        subset=["mean_roc_auc"]
    )

    if depth_df.empty:
        raise RuntimeError(
            "Every tree depth failed during cross-validation."
        )

    best_row = depth_df.loc[
        depth_df["mean_roc_auc"].idxmax()
    ]

    best_depth = int(best_row["depth"])

    print(
        f"\n🏆 Selected Decision Tree Depth: "
        f"{best_depth}"
    )

    # ==========================================================
    # 4. Train the final Decision Tree
    # ==========================================================

    model = DecisionTreeClassifier(
        max_depth=best_depth,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
    )

    model.fit(
        X_train,
        y_train,
    )

    # ==========================================================
    # 5. Generate holdout predictions
    # ==========================================================

    y_pred = model.predict(X_test)

    # Probability of class 1:
    # Demented or Converted
    y_prob = model.predict_proba(X_test)[:, 1]

    # ==========================================================
    # 6. Check for overfitting
    # ==========================================================

    train_accuracy = model.score(
        X_train,
        y_train,
    )

    test_accuracy = model.score(
        X_test,
        y_test,
    )

    print("\n🌳 --- OVERFITTING CHECK ---")
    print(f"Training accuracy: {train_accuracy:.3f}")
    print(f"Testing accuracy : {test_accuracy:.3f}")
    print(
        f"Accuracy gap     : "
        f"{train_accuracy - test_accuracy:.3f}"
    )

    # ==========================================================
    # 7. Holdout test metrics
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

    print("\n✅ --- DECISION TREE PERFORMANCE ---")

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
    # 8. Confusion matrix
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
    # 9. Full group-aware cross-validation
    # ==========================================================

    full_cv = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    cv_auc = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=full_cv,
        scoring="roc_auc",
    )

    cv_accuracy = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=full_cv,
        scoring="accuracy",
    )

    cv_precision = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=full_cv,
        scoring="precision",
    )

    cv_recall = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=full_cv,
        scoring="recall",
    )

    cv_f1 = cross_val_score(
        model,
        X,
        y,
        groups=groups,
        cv=full_cv,
        scoring="f1",
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
    # 10. Feature importance
    # ==========================================================

    importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_,
    }).sort_values(
        "Importance",
        ascending=False,
    )

    print("\nFeature Importance")
    print(importance.to_string(index=False))


if __name__ == "__main__":
    train_decision_tree(
        "data/clinician_view_data/clinician_mri_clean.csv"
    )