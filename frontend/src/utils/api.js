const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

async function handleResponse(response) {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function fetchFlights() {
  const res = await fetch(`${API_URL}/flights`);
  return handleResponse(res);
}

export async function getInsights() {
  const res = await fetch(`${API_URL}/insights`);
  return handleResponse(res);
}

export async function scoreFlight(payload) {
  const res = await fetch(`${API_URL}/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}
