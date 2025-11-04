import os
import requests

LANGFLOW_URL = os.getenv(
    "LANGFLOW_URL", "http://localhost:7860/api/v1/predict/<FLOW_ID>"
)  # Replace <FLOW_ID> with your Langflow flow ID


def generate_explanation(shap_values: dict):
    try:
        text = f"Explain flight delay factors: {shap_values}"
        resp = requests.post(LANGFLOW_URL, json={"inputs": text}, timeout=10)
        if not resp.ok:
            return f"Langflow responded with status {resp.status_code}"
        payload = resp.json()
        outputs = payload.get("outputs") or payload.get("data") or []
        if isinstance(outputs, list) and outputs:
            return outputs[0]
        return "No explanation available"
    except Exception as exc:
        return f"Langflow not reachable: {exc}"
