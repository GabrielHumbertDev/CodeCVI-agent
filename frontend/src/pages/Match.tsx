import { useEffect, useState } from "react";
import { listCVs } from "../api/cvs";
import { listJobs } from "../api/jobs";
import { scoreMatch } from "../api/match";

const gradeColor: Record<string, string> = {
  Excellent: "text-green-600", Good: "text-blue-600",
  Fair: "text-yellow-600", Poor: "text-red-600",
};

const Match = () => {
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

  const handleMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setReport(null);
    try {
      setReport(await scoreMatch(cvId, jobId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Match failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-10 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Match CV to Job</h1>

      <form onSubmit={handleMatch} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
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
          {loading ? "Scoring..." : "Run Match"}
        </button>
      </form>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {report && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-baseline gap-3">
              <span className="text-5xl font-bold text-gray-800">{report.overall_score}%</span>
              <span className={`text-xl font-semibold ${gradeColor[report.grade] ?? ""}`}>{report.grade}</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">{report.explanation}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
              <p className="text-sm font-semibold text-green-700 mb-2">Top Strengths</p>
              <div className="flex flex-wrap gap-1">
                {report.top_strengths.map((s: string) => (
                  <span key={s} className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full">{s}</span>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
              <p className="text-sm font-semibold text-red-700 mb-2">Critical Gaps</p>
              <div className="flex flex-wrap gap-1">
                {report.critical_gaps.map((g: string) => (
                  <span key={g} className="text-xs bg-red-50 text-red-700 border border-red-200 px-2 py-0.5 rounded-full">{g}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className="text-sm font-semibold text-gray-700 mb-3">Category Breakdown</p>
            <div className="space-y-2">
              {report.category_scores.map((cat: any) => (
                <div key={cat.category}>
                  <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                    <span className="capitalize">{cat.category}</span>
                    <span>{cat.score}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${cat.score >= 60 ? "bg-green-500" : cat.score >= 40 ? "bg-yellow-400" : "bg-red-400"}`}
                      style={{ width: `${cat.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Match;
