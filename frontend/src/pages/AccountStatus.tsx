import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../components/AuthContext";

const icons: Record<string, string> = {
  pending: "⏳",
  paused: "⏸️",
  disabled: "🚫",
  default: "⚠️",
};

const AccountStatus = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [message, setMessage] = useState("");

  useEffect(() => {
    const stored = localStorage.getItem("account_status_message");
    if (stored) {
      setMessage(stored);
      localStorage.removeItem("account_status_message");
    }
  }, []);

  const getIcon = () => {
    if (message.includes("pending")) return icons.pending;
    if (message.includes("paused")) return icons.paused;
    if (message.includes("disabled")) return icons.disabled;
    return icons.default;
  };

  const getTitle = () => {
    if (message.includes("pending")) return "Account Pending Approval";
    if (message.includes("paused")) return "Account Paused";
    if (message.includes("disabled")) return "Account Disabled";
    return "Account Access Restricted";
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white rounded-2xl shadow-md p-10 w-full max-w-md text-center space-y-5">
        <div className="text-6xl">{getIcon()}</div>
        <h1 className="text-2xl font-bold text-gray-800">{getTitle()}</h1>
        <p className="text-gray-500 text-sm leading-relaxed">
          {message || "Your account access is currently restricted. Please contact support for assistance."}
        </p>
        <div className="pt-2 space-y-2">
          <button
            onClick={handleLogout}
            className="w-full bg-blue-600 text-white text-sm font-medium py-2 rounded-lg hover:bg-blue-700"
          >
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountStatus;
