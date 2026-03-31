import { useEffect, useState } from "react";
import { listCVs } from "../api/cvs";
import { listJobs } from "../api/jobs";
import { getCoaching } from "../api/analytics";

const priorityColor: Record<string, string> = {
  high: "bg-red-100 text-red-700",
  medium: "bg-yellow-100 text-yellow-700",
};

const Coaching = () => {
  const [cvs, setCVs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [cvId, setCvId] = useState("");
  const [jobId, setJobId] = useState("");
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listCVs().then((d) => setCVs(d.cvs));
    listJobs().then((d) => setJobs(d.jobs));
  }, []);

  const handleCoach = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setReport(null);
    try {
      setReport(await getCoaching(cvId, jobId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Coaching failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-10 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Coaching Tips</h1>

      <form onSubmit={handleCoach} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select CV</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={cvId} onChange={(e) => setCvId(e.target.value)} required>
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
          {loading ? "Analysing..." : "Get Coaching Tips"}
        </button>
      </form>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {report && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-baseline gap-3 mb-2">
              <span className="text-4xl font-bold text-gray-800">{report.overall_score}%</span>
              <span className="text-lg font-medium text-gray-500">{report.grade}</span>
            </div>
            <p className="text-sm text-gray-600">{report.headline}</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {report.category_scores.map((cat: any) => (
              <div key={cat.category} className="bg-white rounded-xl border border-gray-100 shadow-sm p-3 text-center">
                <p className="text-xs text-gray-500 capitalize">{cat.category}</p>
                <p className="text-2xl font-bold text-gray-800 mt-1">{cat.score}%</p>
                <p className="text-xs text-gray-400">{cat.matched_count} matched · {cat.missing_count} missing</p>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-3">
            <h2 className="text-sm font-semibold text-gray-700">Actionable Tips</h2>
            {report.tips.map((tip: any, i: number) => (
              <div key={i} className="flex gap-3 items-start border-b border-gray-50 pb-3 last:border-0 last:pb-0">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium mt-0.5 shrink-0 ${priorityColor[tip.priority] ?? "bg-gray-100 text-gray-600"}`}>
                  {tip.priority}
                </span>
                <div>
                  <p className="text-xs text-gray-400 capitalize">{tip.category} · <span className="font-medium text-gray-600">{tip.gap}</span></p>
                  <p className="text-sm text-gray-700 mt-0.5">{tip.tip}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Coaching;
