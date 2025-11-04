def explain_prediction(features):
    shap = {
        "crosswind": round(0.2 * (features.get("wind", 0) / 20), 2),
        "visibility": round(
            -0.15 * ((features.get("visibility", 10) - 10) / 10), 2
        ),
        "atc": round(0.1 * (features.get("atc", 0) / 10), 2),
    }
    return shap
