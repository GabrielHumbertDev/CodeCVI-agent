import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../components/AuthContext";
import { exportMyData, getAuditLog, updateConsent, deleteMyAccount } from "../api/gdpr";

const GDPR = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [auditLog, setAuditLog] = useState<any[]>([]);
  const [showLog, setShowLog] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleExport = async () => {
    try {
      const data = await exportMyData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "my_data.json"; a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Export failed.");
    }
  };

  const handleAuditLog = async () => {
    if (showLog) { setShowLog(false); return; }
    try {
      const logs = await getAuditLog();
      setAuditLog(logs);
      setShowLog(true);
    } catch {
      setError("Failed to load audit log.");
    }
  };

  const handleConsent = async (consent: boolean) => {
    try {
      await updateConsent(consent);
      setSuccess(`Consent ${consent ? "granted" : "withdrawn"} successfully.`);
    } catch {
      setError("Consent update failed.");
    }
  };

  const handleDelete = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!window.confirm("This will permanently delete your account and all data. Are you sure?")) return;
    try {
      await deleteMyAccount(deletePassword);
      logout();
      navigate("/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Account deletion failed.");
    }
  };

  return (
    <div className="py-10 space-y-6 max-w-2xl">
      <h1 className="text-3xl font-bold text-gray-800">Privacy & GDPR</h1>

      {error && <p className="text-red-500 text-sm">{error}</p>}
      {success && <p className="text-green-600 text-sm">{success}</p>}

      {/* Export */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <h2 className="font-semibold text-gray-800 mb-1">Right of Access (Art. 15)</h2>
        <p className="text-sm text-gray-500 mb-3">Download all personal data we hold about you.</p>
        <button onClick={handleExport} className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700">
          Download My Data
        </button>
      </div>

      {/* Audit log */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <h2 className="font-semibold text-gray-800 mb-1">Audit Log</h2>
        <p className="text-sm text-gray-500 mb-3">View all actions recorded on your account.</p>
        <button onClick={handleAuditLog} className="bg-gray-100 text-gray-700 text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-200">
          {showLog ? "Hide Log" : "View Audit Log"}
        </button>
        {showLog && (
          <div className="mt-4 space-y-1 max-h-60 overflow-y-auto">
            {auditLog.length === 0 ? (
              <p className="text-sm text-gray-400">No entries.</p>
            ) : auditLog.map((log) => (
              <div key={log.id} className="text-xs text-gray-600 border-b border-gray-50 py-1">
                <span className="font-medium">{log.action}</span>
                {log.entity_type && <span className="text-gray-400"> · {log.entity_type}</span>}
                <span className="text-gray-400 float-right">{new Date(log.created_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Consent */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <h2 className="font-semibold text-gray-800 mb-1">Consent Management</h2>
        <p className="text-sm text-gray-500 mb-3">Update your GDPR consent status.</p>
        <div className="flex gap-3">
          <button onClick={() => handleConsent(true)} className="bg-green-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-green-700">Grant Consent</button>
          <button onClick={() => handleConsent(false)} className="bg-gray-200 text-gray-700 text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-300">Withdraw Consent</button>
        </div>
      </div>

      {/* Delete account */}
      <div className="bg-white rounded-xl border border-red-100 shadow-sm p-5">
        <h2 className="font-semibold text-red-700 mb-1">Right to Erasure (Art. 17)</h2>
        <p className="text-sm text-gray-500 mb-3">Permanently delete your account and all associated data. This cannot be undone.</p>
        <form onSubmit={handleDelete} className="space-y-3">
          <input
            type="password"
            placeholder="Confirm your password"
            className="w-full border border-red-200 rounded-lg px-3 py-2 text-sm"
            value={deletePassword}
            onChange={(e) => setDeletePassword(e.target.value)}
            required
          />
          <button type="submit" className="bg-red-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-red-700">
            Delete My Account
          </button>
        </form>
      </div>
    </div>
  );
};

export default GDPR;
