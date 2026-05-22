import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listCVs } from "../api/cvs";
import { listJobs } from "../api/jobs";
import { listVersions } from "../api/tailor";
import { listCoverLettersByJob } from "../api/coverLetters";
import { downloadDocx, downloadPdf } from "../api/export";

const DIRECT_TOOLS = [
  { to: "/match", label: "Match", detail: "Run the old standalone match view." },
  { to: "/tailor", label: "Tailor", detail: "Generate and browse CV versions by CV." },
  { to: "/cover-letters", label: "Cover Letters", detail: "Generate and browse letters by job." },
  { to: "/coaching", label: "Coaching", detail: "Open the standalone coaching view." },
];

const History = () => {
  const [cvs, setCvs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [cvId, setCvId] = useState("");
  const [jobId, setJobId] = useState("");
  const [versions, setVersions] = useState<any[]>([]);
  const [letters, setLetters] = useState<any[]>([]);
  const [expandedLetter, setExpandedLetter] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([listCVs(), listJobs()])
      .then(([cvData, jobData]) => {
        setCvs(cvData.cvs);
        setJobs(jobData.jobs);
      })
      .catch(() => setError("Could not load history sources."));
  }, []);

  const handleCvChange = async (id: string) => {
    setCvId(id);
    setVersions([]);
    if (!id) return;
    try {
      setVersions(await listVersions(id));
    } catch {
      setError("Could not load tailored CV versions.");
    }
  };

  const handleJobChange = async (id: string) => {
    setJobId(id);
    setLetters([]);
    setExpandedLetter("");
    if (!id) return;
    try {
      setLetters(await listCoverLettersByJob(id));
    } catch {
      setError("Could not load cover letters.");
    }
  };

  return (
    <div className="py-10 space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Generated documents</p>
        <h1 className="text-3xl font-bold text-gray-900">History</h1>
      </div>

      {error && <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">{error}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5 space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Tailored CV versions</h2>
          <select
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            value={cvId}
            onChange={(event) => handleCvChange(event.target.value)}
          >
            <option value="">Select a CV</option>
            {cvs.map((cv) => (
              <option key={cv.id} value={cv.id}>{cv.filename}</option>
            ))}
          </select>

          {cvId && versions.length === 0 && <p className="text-sm text-gray-400">No tailored versions for this CV yet.</p>}

          <div className="space-y-3">
            {versions.map((version) => (
              <div key={version.id} className="border border-gray-100 rounded-lg p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-800">Version {version.version_number}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(version.created_at).toLocaleString()} - {version.validation_passed ? "Validated" : "Needs review"}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => downloadDocx(version.id)} className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-md">DOCX</button>
                  <button onClick={() => downloadPdf(version.id)} className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-md">PDF</button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5 space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Cover letters</h2>
          <select
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            value={jobId}
            onChange={(event) => handleJobChange(event.target.value)}
          >
            <option value="">Select a job</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>{job.title}{job.company ? ` - ${job.company}` : ""}</option>
            ))}
          </select>

          {jobId && letters.length === 0 && <p className="text-sm text-gray-400">No cover letters for this job yet.</p>}

          <div className="space-y-3">
            {letters.map((letter) => (
              <div key={letter.id} className="border border-gray-100 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800">Version {letter.version_number}</p>
                    <p className="text-xs text-gray-400">{new Date(letter.created_at).toLocaleString()}</p>
                  </div>
                  <button
                    onClick={() => setExpandedLetter(expandedLetter === letter.id ? "" : letter.id)}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    {expandedLetter === letter.id ? "Hide" : "View"}
                  </button>
                </div>
                {expandedLetter === letter.id && (
                  <pre className="mt-3 border-t border-gray-100 pt-3 text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                    {letter.content}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Advanced direct tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {DIRECT_TOOLS.map((tool) => (
            <Link key={tool.to} to={tool.to} className="border border-gray-100 rounded-lg p-3 hover:border-blue-200 hover:bg-blue-50 transition-colors">
              <p className="text-sm font-semibold text-gray-800">{tool.label}</p>
              <p className="text-xs text-gray-500 mt-1">{tool.detail}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
};

export default History;
