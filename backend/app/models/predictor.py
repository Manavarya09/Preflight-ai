import random


def predict_delay(features):
    prob = min(
        1,
        0.2
        + 0.03 * features.get("wind", 0)
        + 0.02 * (10 - features.get("visibility", 10))
        + 0.01 * features.get("atc", 0)
        + random.random() * 0.1,
    )
    delay = int(prob * 40)
    return round(prob, 2), delay
