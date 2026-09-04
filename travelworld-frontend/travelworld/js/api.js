// API CONFIG
const BASE_URL = "http://localhost:5000/api/v1";

// API HELPER
async function apiRequest(endpoint, method = "GET", body = null) {
  try {
    const headers = {
      "Content-Type": "application/json",
    };
    const token = localStorage.getItem("token");
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const options = {
      method,
      credentials: "include", // send cookies
      headers,
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 35000);
    options.signal = controller.signal;

    let response;
    try {
      response = await fetch(`${BASE_URL}${endpoint}`, options);
    } finally {
      clearTimeout(timeoutId);
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error("API Request failed:", error);
    throw error;
  }
}
