import { useEffect, useState } from "react";
import { createJob, listJobs, deleteJob } from "../api/jobs";

const Jobs = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () =>
    listJobs()
      .then((d) => setJobs(d.jobs))
      .catch(() => setError("Failed to load jobs."))
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await createJob({ title, company, description });
      setTitle(""); setCompany(""); setDescription("");
      setShowForm(false);
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create job.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this job?")) return;
    try {
      await deleteJob(id);
      setJobs((prev) => prev.filter((j) => j.id !== id));
    } catch {
      setError("Delete failed.");
    }
  };

  return (
    <div className="py-10 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">Jobs</h1>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "+ Add Job"}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Job title *</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
            <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={company} onChange={(e) => setCompany(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Job description *</label>
            <textarea rows={5} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={description} onChange={(e) => setDescription(e.target.value)} required />
          </div>
          <button type="submit" disabled={saving} className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Saving..." : "Save Job"}
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : jobs.length === 0 ? (
        <p className="text-gray-400">No jobs added yet.</p>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-start justify-between">
              <div>
                <p className="font-medium text-gray-800">{job.title}</p>
                {job.company && <p className="text-sm text-gray-500">{job.company}</p>}
                <p className="text-xs text-gray-400 mt-1">{new Date(job.created_at).toLocaleDateString()}</p>
              </div>
              <button onClick={() => handleDelete(job.id)} className="text-sm text-red-500 hover:text-red-700 mt-1">
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Jobs;
