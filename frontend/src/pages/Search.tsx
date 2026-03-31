import { useEffect, useState } from "react";
import { listCVs } from "../api/cvs";
import { listJobs } from "../api/jobs";
import { searchJobsForCV, searchCVsForJob } from "../api/search";

const Search = () => {
  const [cvs, setCVs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [mode, setMode] = useState<"jobs-for-cv" | "cvs-for-job">("jobs-for-cv");
  const [cvId, setCvId] = useState("");
  const [jobId, setJobId] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listCVs().then((d) => setCVs(d.cvs));
    listJobs().then((d) => setJobs(d.jobs));
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setResults([]);
    try {
      const data = mode === "jobs-for-cv"
        ? await searchJobsForCV(cvId)
        : await searchCVsForJob(jobId);
      setResults(data.results ?? []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Search failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-10 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Semantic Search</h1>

      <div className="flex gap-2">
        {(["jobs-for-cv", "cvs-for-job"] as const).map((m) => (
          <button
            key={m}
            onClick={() => { setMode(m); setResults([]); }}
            className={`text-sm px-4 py-2 rounded-lg font-medium ${mode === m ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            {m === "jobs-for-cv" ? "Find jobs for my CV" : "Find CVs for a job"}
          </button>
        ))}
      </div>

      <form onSubmit={handleSearch} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
        {mode === "jobs-for-cv" ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select CV</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={cvId} onChange={(e) => setCvId(e.target.value)} required>
              <option value="">-- choose CV --</option>
              {cvs.map((c) => <option key={c.id} value={c.id}>{c.filename}</option>)}
            </select>
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Job</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={jobId} onChange={(e) => setJobId(e.target.value)} required>
              <option value="">-- choose job --</option>
              {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
            </select>
          </div>
        )}
        <button type="submit" disabled={loading} className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {results.length > 0 && (
        <div className="space-y-3">
          {results.map((r, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex justify-between items-center">
              <p className="font-medium text-gray-800">{r.title ?? r.filename ?? r.id}</p>
              <span className="text-sm font-semibold text-blue-600">{Math.round((r.similarity ?? 0) * 100)}% match</span>
            </div>
          ))}
        </div>
      )}
      {!loading && results.length === 0 && <p className="text-gray-400 text-sm">No results yet.</p>}
    </div>
  );
};

export default Search;
