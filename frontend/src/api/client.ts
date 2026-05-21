import axios from "axios";

const client = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "/api/v1",
});

// Inject token on every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle account restriction mid-session
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail ?? "";

    // 403 with an account restriction message → redirect to /account-status
    if (status === 403 && typeof detail === "string" && (
      detail.includes("pending") ||
      detail.includes("paused") ||
      detail.includes("disabled") ||
      detail.includes("restricted")
    )) {
      // Store the message so the status page can display it
      localStorage.setItem("account_status_message", detail);
      window.location.href = "/account-status";
    }

    return Promise.reject(error);
  }
);

export default client;
