import { useEffect, useState } from "react";
import { listCVs } from "../api/cvs";
import { listJobs } from "../api/jobs";
import { tailorCV, listVersions } from "../api/tailor";
import { downloadDocx, downloadPdf } from "../api/export";

const Tailor = () => {
  const [cvs, setCVs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [cvId, setCvId] = useState("");
  const [jobId, setJobId] = useState("");
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    listCVs().then((d) => setCVs(d.cvs));
    listJobs().then((d) => setJobs(d.jobs));
  }, []);

  const loadVersions = (id: string) =>
    listVersions(id).then(setVersions).catch(() => {});

  const handleCVChange = (id: string) => {
    setCvId(id);
    setVersions([]);
    if (id) loadVersions(id);
  };

  const handleTailor = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setSuccess("");
    try {
      await tailorCV(cvId, jobId);
      setSuccess("CV tailored successfully!");
      await loadVersions(cvId);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Tailoring failed. Is Ollama running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-10 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Tailor CV</h1>

      <form onSubmit={handleTailor} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select CV</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={cvId} onChange={(e) => handleCVChange(e.target.value)} required>
              <option value="">-- choose CV --</option>
              {cvs.map((c) => <option key={c.id} value={c.id}>{c.filename}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Job</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={jobId} onChange={(e) => setJobId(e.target.value)} required>
              <option value="">-- choose job --</option>
              {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}{j.company ? ` — ${j.company}` : ""}</option>)}
            </select>
          </div>
        </div>
        <button type="submit" disabled={loading} className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Tailoring (this takes ~30s)..." : "Tailor CV"}
        </button>
      </form>

      {error && <p className="text-red-500 text-sm">{error}</p>}
      {success && <p className="text-green-600 text-sm">{success}</p>}

      {versions.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-700">Tailored Versions</h2>
          {versions.map((v) => (
            <div key={v.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-800">Version {v.version_number}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {new Date(v.created_at).toLocaleString()} ·{" "}
                  <span className={v.validation_passed ? "text-green-600" : "text-yellow-600"}>
                    {v.validation_passed ? "Validated" : "Unvalidated"}
                  </span>
                </p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => downloadDocx(v.id)} className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg">DOCX</button>
                <button onClick={() => downloadPdf(v.id)} className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg">PDF</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Tailor;
