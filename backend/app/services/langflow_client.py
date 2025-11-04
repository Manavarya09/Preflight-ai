import os
import requests

LANGFLOW_URL = os.getenv(
    "LANGFLOW_URL", "http://localhost:7860/api/v1/predict/<FLOW_ID>"
)  # Replace <FLOW_ID> with your Langflow flow ID


def generate_explanation(shap_values: dict):
    try:
        payload = {"inputs": shap_values}
        resp = requests.post(LANGFLOW_URL, json=payload, timeout=15)
        if not resp.ok:
            return {
                "error": f"Langflow responded with status {resp.status_code}",
                "details": resp.text,
            }
        return resp.json()
    except Exception as exc:
        return {"error": f"Langflow not reachable: {exc}"}
