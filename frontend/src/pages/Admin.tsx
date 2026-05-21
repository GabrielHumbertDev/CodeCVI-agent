import { useEffect, useState } from "react";
import {
  listUsers, approveUser, pauseUser, resumeUser,
  disableUser, deleteUser, editUser,
} from "../api/admin";

const STATUS_TABS = ["all", "pending_approval", "active", "paused", "disabled"];

const statusBadge = (status: string) => {
  const styles: Record<string, string> = {
    active: "bg-green-100 text-green-700",
    pending_approval: "bg-yellow-100 text-yellow-700",
    paused: "bg-orange-100 text-orange-700",
    disabled: "bg-red-100 text-red-700",
  };
  const labels: Record<string, string> = {
    pending_approval: "Pending",
    active: "Active",
    paused: "Paused",
    disabled: "Disabled",
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${styles[status] ?? "bg-gray-100 text-gray-600"}`}>
      {labels[status] ?? status}
    </span>
  );
};

const roleBadge = (role: string) => (
  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${role === "admin" ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-500"}`}>
    {role}
  </span>
);

const Admin = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [search, setSearch] = useState("");
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [pauseReason, setPauseReason] = useState("");
  const [pausingId, setPausingId] = useState<string | null>(null);
  const [editingUser, setEditingUser] = useState<any | null>(null);
  const [editForm, setEditForm] = useState({ full_name: "", email: "", role: "", new_password: "" });

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const params: any = { include_deleted: includeDeleted };
      if (activeTab !== "all") params.status = activeTab;
      if (search) params.search = search;
      setUsers(await listUsers(params));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load users.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [activeTab, includeDeleted]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    load();
  };

  const action = async (fn: () => Promise<any>, confirmMsg?: string) => {
    if (confirmMsg && !window.confirm(confirmMsg)) return;
    setError("");
    try {
      await fn();
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Action failed.");
    }
  };

  const handlePause = async (id: string) => {
    await action(() => pauseUser(id, pauseReason));
    setPausingId(null);
    setPauseReason("");
  };

  const openEdit = (user: any) => {
    setEditingUser(user);
    setEditForm({ full_name: user.full_name ?? "", email: user.email, role: user.role, new_password: "" });
  };

  const handleEdit = async () => {
    if (!editingUser) return;
    const payload: any = { full_name: editForm.full_name, email: editForm.email, role: editForm.role };
    if (editForm.new_password) payload.new_password = editForm.new_password;
    await action(() => editUser(editingUser.id, payload));
    setEditingUser(null);
  };

  return (
    <div className="py-10 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Admin — User Management</h1>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {/* Tabs */}
      <div className="flex gap-2 flex-wrap">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`text-sm px-4 py-1.5 rounded-full font-medium capitalize ${activeTab === tab ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            {tab === "all" ? "All Users" : tab === "pending_approval" ? "Pending Approval" : tab}
          </button>
        ))}
      </div>

      {/* Search + filters */}
      <form onSubmit={handleSearch} className="flex gap-3 items-center flex-wrap">
        <input
          type="text"
          placeholder="Search by name or email..."
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit" className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700">
          Search
        </button>
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input type="checkbox" checked={includeDeleted} onChange={(e) => setIncludeDeleted(e.target.checked)} />
          Include deleted
        </label>
      </form>

      {/* User table */}
      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : users.length === 0 ? (
        <p className="text-gray-400">No users found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm bg-white rounded-xl shadow-sm border border-gray-100">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b border-gray-100">
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Registered</th>
                <th className="px-4 py-3">Last Login</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className={`border-b border-gray-50 hover:bg-gray-50 ${user.is_deleted ? "opacity-40" : ""}`}>
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-800">{user.full_name ?? "—"}</p>
                    <p className="text-xs text-gray-400">{user.email}</p>
                  </td>
                  <td className="px-4 py-3">{roleBadge(user.role)}</td>
                  <td className="px-4 py-3">{statusBadge(user.status)}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{new Date(user.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : "Never"}
                  </td>
                  <td className="px-4 py-3">
                    {!user.is_deleted && (
                      <div className="flex gap-1 flex-wrap">
                        {user.status === "pending_approval" && (
                          <button onClick={() => action(() => approveUser(user.id))} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200">
                            Approve
                          </button>
                        )}
                        {user.status === "active" && (
                          <button onClick={() => setPausingId(user.id)} className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded hover:bg-orange-200">
                            Pause
                          </button>
                        )}
                        {user.status === "paused" && (
                          <button onClick={() => action(() => resumeUser(user.id))} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200">
                            Resume
                          </button>
                        )}
                        {user.status !== "disabled" && (
                          <button onClick={() => action(() => disableUser(user.id), "Disable this user?")} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200">
                            Disable
                          </button>
                        )}
                        <button onClick={() => openEdit(user)} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200">
                          Edit
                        </button>
                        <button onClick={() => action(() => deleteUser(user.id), "Soft-delete this user? They will be disabled and hidden.")} className="text-xs bg-red-50 text-red-400 px-2 py-1 rounded hover:bg-red-100">
                          Delete
                        </button>
                      </div>
                    )}
                    {user.is_deleted && <span className="text-xs text-gray-400 italic">Deleted</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pause reason modal */}
      {pausingId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-sm space-y-4">
            <h2 className="font-semibold text-gray-800">Pause User</h2>
            <textarea
              rows={3}
              placeholder="Reason (optional)"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              value={pauseReason}
              onChange={(e) => setPauseReason(e.target.value)}
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => { setPausingId(null); setPauseReason(""); }} className="text-sm px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">Cancel</button>
              <button onClick={() => handlePause(pausingId)} className="text-sm px-4 py-2 rounded-lg bg-orange-500 text-white hover:bg-orange-600">Pause</button>
            </div>
          </div>
        </div>
      )}

      {/* Edit modal */}
      {editingUser && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-sm space-y-4">
            <h2 className="font-semibold text-gray-800">Edit User</h2>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Full name</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={editForm.full_name} onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Email</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={editForm.email} onChange={(e) => setEditForm({ ...editForm, email: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Role</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={editForm.role} onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}>
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">New Password <span className="text-gray-400 font-normal">(leave blank to keep current)</span></label>
              <input
                type="password"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="Min. 8 characters"
                value={editForm.new_password}
                onChange={(e) => setEditForm({ ...editForm, new_password: e.target.value })}
              />
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setEditingUser(null)} className="text-sm px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">Cancel</button>
              <button onClick={handleEdit} className="text-sm px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700">Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;
