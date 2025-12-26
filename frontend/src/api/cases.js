const API_URL = "http://127.0.0.1:8000";

export async function createCase(payload) {
  const res = await fetch(`${API_URL}/cases`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Failed to create case");
  }

  return res.json();
}
