import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# -----------------------------
# 1. LOAD DATASET
# -----------------------------

data = pd.read_csv("ml/dataset/candidate_dataset.csv")

print("Dataset loaded successfully!")
print("Shape:", data.shape)


# -----------------------------
# 2. SELECT FEATURES AND TARGET
# -----------------------------

features = [
    "required_skill_match",
    "preferred_skill_match",
    "total_skill_match",
    "matched_required_count",
    "matched_preferred_count",
    "experience_years",
    "project_count"
]

X = data[features]
y = data["shortlisted"]


# -----------------------------
# 3. SPLIT DATA
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# -----------------------------
# 4. DEFINE MODELS
# -----------------------------

models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(random_state=42))
    ]),

    "Decision Tree": DecisionTreeClassifier(
        random_state=42,
        max_depth=6
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=8
    )
}


# -----------------------------
# 5. TRAIN AND EVALUATE MODELS
# -----------------------------

results = {}

for name, model in models.items():

    print(f"\nTraining {name}...")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)

    results[name] = {
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")


# -----------------------------
# 6. SELECT BEST MODEL
# -----------------------------

best_model_name = max(
    results,
    key=lambda name: results[name]["f1"]
)

best_model = results[best_model_name]["model"]

print("\n" + "=" * 40)
print("BEST MODEL:", best_model_name)
print("Best F1 Score:", results[best_model_name]["f1"])
print("=" * 40)


# -----------------------------
# 7. SAVE MODEL
# -----------------------------

model_path = "ml/models/candidate_shortlisting_model.pkl"

joblib.dump(best_model, model_path)

print("\nModel saved successfully!")
print("Saved at:", model_path)


# -----------------------------
# 8. SAVE FEATURE NAMES
# -----------------------------

feature_path = "ml/models/features.pkl"

joblib.dump(features, feature_path)

print("Features saved successfully!")