from pathlib import Path
import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "candidate_shortlisting_model.pkl"
)

FEATURE_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "features.pkl"
)


model = joblib.load(MODEL_PATH)

features = joblib.load(FEATURE_PATH)


def predict_candidate(features_data: dict):

    input_data = pd.DataFrame(
        [features_data]
    )

    input_data = input_data[features]

    prediction = model.predict(
        input_data
    )[0]

    probability = model.predict_proba(
        input_data
    )[0][1]

    return {
        "prediction": int(prediction),
        "probability": round(
            float(probability) * 100,
            2
        ),
    }
