import { useEffect, useState } from "react";
import { listCVs } from "../api/cvs";
import { listJobs } from "../api/jobs";
import { generateCoverLetter, listCoverLettersByJob } from "../api/coverLetters";

const CoverLetters = () => {
  const [cvs, setCVs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [letters, setLetters] = useState<any[]>([]);
  const [cvId, setCvId] = useState("");
  const [jobId, setJobId] = useState("");
  const [filterJobId, setFilterJobId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    listCVs().then((d) => setCVs(d.cvs));
    listJobs().then((d) => setJobs(d.jobs));
  }, []);

  const handleJobFilter = (id: string) => {
    setFilterJobId(id);
    setLetters([]);
    if (id) listCoverLettersByJob(id).then(setLetters);
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const letter = await generateCoverLetter(cvId, jobId);
      setLetters((prev) => [letter, ...prev]);
      if (!filterJobId) setFilterJobId(jobId);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Generation failed. Is Ollama running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-10 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Cover Letters</h1>

      <form onSubmit={handleGenerate} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">CV (parsed)</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={cvId} onChange={(e) => setCvId(e.target.value)} required>
              <option value="">-- choose CV --</option>
              {cvs.map((c) => <option key={c.id} value={c.id}>{c.filename}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Job</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={jobId} onChange={(e) => setJobId(e.target.value)} required>
              <option value="">-- choose job --</option>
              {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}{j.company ? ` — ${j.company}` : ""}</option>)}
            </select>
          </div>
        </div>
        <button type="submit" disabled={loading} className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Generating (~30s)..." : "Generate Cover Letter"}
        </button>
      </form>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {/* View letters by job */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">View letters for job</label>
        <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm" value={filterJobId} onChange={(e) => handleJobFilter(e.target.value)}>
          <option value="">-- select job --</option>
          {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
        </select>
      </div>

      {letters.length > 0 && (
        <div className="space-y-3">
          {letters.map((letter) => (
            <div key={letter.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
              <div className="flex justify-between items-center">
                <p className="font-medium text-gray-800 text-sm">
                  Version {letter.version_number} · {new Date(letter.created_at).toLocaleDateString()}
                </p>
                <button
                  onClick={() => setExpanded(expanded === letter.id ? null : letter.id)}
                  className="text-xs text-blue-600 hover:underline"
                >
                  {expanded === letter.id ? "Hide" : "View"}
                </button>
              </div>
              {expanded === letter.id && (
                <pre className="mt-3 text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed border-t border-gray-100 pt-3">
                  {letter.content}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CoverLetters;
