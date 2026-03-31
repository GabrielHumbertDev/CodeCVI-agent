import { useEffect, useState } from "react";
import { listJobs } from "../api/jobs";
import {
  createApplication, listApplications, updateApplication,
  deleteApplication, getReadiness,
} from "../api/applications";

const STATUSES = ["draft", "applied", "interview", "offer", "rejected", "withdrawn"];
const statusColor: Record<string, string> = {
  draft: "bg-gray-100 text-gray-600",
  applied: "bg-blue-100 text-blue-700",
  interview: "bg-yellow-100 text-yellow-700",
  offer: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  withdrawn: "bg-gray-100 text-gray-400",
};

const Applications = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [apps, setApps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [jobId, setJobId] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [readiness, setReadiness] = useState<Record<string, any>>({});

  const load = () =>
    listApplications()
      .then(setApps)
      .catch(() => setError("Failed to load applications."))
      .finally(() => setLoading(false));

  useEffect(() => {
    listJobs().then((d) => setJobs(d.jobs));
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createApplication({ job_id: jobId, notes });
      setJobId(""); setNotes(""); setShowForm(false);
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create.");
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      const updated = await updateApplication(id, { status });
      setApps((prev) => prev.map((a) => a.id === id ? updated : a));
    } catch {
      setError("Status update failed.");
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this application?")) return;
    try {
      await deleteApplication(id);
      setApps((prev) => prev.filter((a) => a.id !== id));
    } catch {
      setError("Delete failed.");
    }
  };

  const toggleReadiness = async (id: string) => {
    if (readiness[id]) {
      setReadiness((prev) => { const r = { ...prev }; delete r[id]; return r; });
      return;
    }
    try {
      const r = await getReadiness(id);
      setReadiness((prev) => ({ ...prev, [id]: r }));
    } catch {
      setError("Readiness check failed.");
    }
  };

  const jobTitle = (id: string) => jobs.find((j) => j.id === id)?.title ?? id.slice(0, 8);

  return (
    <div className="py-10 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">Applications</h1>
        <button onClick={() => setShowForm((v) => !v)} className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700">
          {showForm ? "Cancel" : "+ New Application"}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Job *</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={jobId} onChange={(e) => setJobId(e.target.value)} required>
              <option value="">-- select job --</option>
              {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}{j.company ? ` — ${j.company}` : ""}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
          <button type="submit" disabled={saving} className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Saving..." : "Create"}
          </button>
        </form>
      )}

      {loading ? <p className="text-gray-400">Loading...</p> : apps.length === 0 ? (
        <p className="text-gray-400">No applications yet.</p>
      ) : (
        <div className="space-y-3">
          {apps.map((app) => (
            <div key={app.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-gray-800">{jobTitle(app.job_id)}</p>
                  <p className="text-xs text-gray-400">{new Date(app.created_at).toLocaleDateString()}</p>
                  {app.notes && <p className="text-sm text-gray-500 mt-1">{app.notes}</p>}
                </div>
                <div className="flex gap-2 items-center">
                  <select
                    value={app.status}
                    onChange={(e) => handleStatusChange(app.id, e.target.value)}
                    className={`text-xs font-medium px-2 py-1 rounded-full border-0 cursor-pointer ${statusColor[app.status]}`}
                  >
                    {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <button onClick={() => toggleReadiness(app.id)} className="text-xs text-blue-600 hover:underline">Readiness</button>
                  <button onClick={() => handleDelete(app.id)} className="text-xs text-red-500 hover:text-red-700">Delete</button>
                </div>
              </div>

              {readiness[app.id] && (
                <div className="border-t border-gray-100 pt-3 space-y-1">
                  <p className="text-xs font-semibold text-gray-600 mb-2">
                    Readiness: {readiness[app.id].overall_ready ? "✅ Ready" : "⚠️ Not ready"}
                    {readiness[app.id].match_score != null && ` · Match: ${readiness[app.id].match_score}% (${readiness[app.id].match_grade})`}
                  </p>
                  {readiness[app.id].checklist.map((item: any) => (
                    <p key={item.item} className={`text-xs ${item.done ? "text-green-600" : "text-gray-400"}`}>
                      {item.done ? "✓" : "○"} {item.item}
                    </p>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Applications;
