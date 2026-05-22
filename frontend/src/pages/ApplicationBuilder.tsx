import { useEffect, useMemo, useRef, useState } from "react";
import { uploadCV, listCVs } from "../api/cvs";
import { createJob, listJobs } from "../api/jobs";
import { scoreMatch } from "../api/match";
import { tailorCV } from "../api/tailor";
import { generateCoverLetter } from "../api/coverLetters";
import { downloadDocx, downloadPdf } from "../api/export";
import { getCoaching } from "../api/analytics";

const gradeColor: Record<string, string> = {
  Excellent: "text-green-600",
  Good: "text-blue-600",
  Fair: "text-yellow-600",
  Poor: "text-red-600",
};

const emptyJobForm = {
  title: "",
  company: "",
  description: "",
};

const extractBullets = (text: string, cues: string[]) => {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.replace(/^[-*]\s*/, "").trim())
    .filter(Boolean);

  return lines
    .filter((line) => cues.some((cue) => line.toLowerCase().includes(cue)))
    .slice(0, 6);
};

const parseJobDescription = (description: string) => ({
  required: extractBullets(description, ["required", "must", "essential", "minimum", "need"]),
  niceToHave: extractBullets(description, ["nice", "preferred", "desirable", "bonus", "advantage"]),
  responsibilities: extractBullets(description, ["responsible", "deliver", "build", "manage", "support", "develop"]),
  seniority:
    description.match(/\b(senior|lead|principal|junior|graduate|entry.level|mid.level)\b/i)?.[0] ??
    "Not detected",
});

const buildRecommendations = (report: any) => {
  if (!report) return [];
  const categoryAdvice = (report.category_scores ?? [])
    .filter((category: any) => category.score < 60)
    .map((category: any) => ({
      title: `Strengthen ${category.category}`,
      detail: `This section scored ${category.score}%. Emphasise matching evidence already present in your CV before adding anything new.`,
    }));

  const gapAdvice = (report.critical_gaps ?? []).slice(0, 6).map((gap: string) => ({
    title: `Address "${gap}"`,
    detail: "Mention this only if it is genuinely supported by your existing experience, skills, or education.",
  }));

  return [...categoryAdvice, ...gapAdvice].slice(0, 8);
};

const sectionText = (data: any, section: "summary" | "skills" | "experience") => {
  if (!data) return "Not available";
  if (section === "summary") return data.summary || "No summary detected.";
  if (section === "skills") return (data.skills ?? []).join(", ") || "No skills detected.";
  const experience = data.experience ?? [];
  if (!experience.length) return "No experience detected.";
  return experience
    .map((item: any) => {
      const title = [item.title, item.company].filter(Boolean).join(" at ");
      const detail = item.description || (item.bullets ?? []).join(" ");
      return [title, detail].filter(Boolean).join(": ");
    })
    .join("\n\n");
};

const downloadCoverLetterText = (content: string) => {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "cover-letter.txt";
  a.click();
  URL.revokeObjectURL(url);
};

const ApplicationBuilder = () => {
  const [cvs, setCvs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [cvId, setCvId] = useState("");
  const [jobId, setJobId] = useState("");
  const [jobForm, setJobForm] = useState(emptyJobForm);
  const [report, setReport] = useState<any>(null);
  const [tailoredVersion, setTailoredVersion] = useState<any>(null);
  const [coverLetter, setCoverLetter] = useState<any>(null);
  const [coaching, setCoaching] = useState<any>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const selectedCv = useMemo(() => cvs.find((cv) => cv.id === cvId), [cvs, cvId]);
  const selectedJob = useMemo(() => jobs.find((job) => job.id === jobId), [jobs, jobId]);
  const jobInsights = useMemo(
    () => parseJobDescription(selectedJob?.description || jobForm.description || ""),
    [selectedJob, jobForm.description]
  );
  const recommendations = useMemo(() => buildRecommendations(report), [report]);

  const refresh = async () => {
    const [cvData, jobData] = await Promise.all([listCVs(), listJobs()]);
    setCvs(cvData.cvs);
    setJobs(jobData.jobs);
  };

  useEffect(() => {
    refresh().catch(() => setError("Could not load your CVs and jobs."));
  }, []);

  const resetOutputs = () => {
    setReport(null);
    setTailoredVersion(null);
    setCoverLetter(null);
    setCoaching(null);
    setNotice("");
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy("upload");
    setError("");
    resetOutputs();
    try {
      const cv = await uploadCV(file);
      await refresh();
      setCvId(cv.id);
      setNotice("CV uploaded and parsed.");
    } catch (err: any) {
      setError(err.response?.data?.detail || "CV upload failed.");
    } finally {
      setBusy("");
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleCoaching = async () => {
    setBusy("coaching");
    setError("");
    setCoaching(null);
    try {
      setCoaching(await getCoaching(cvId, jobId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not generate coaching tips.");
    } finally {
      setBusy("");
    }
  };

  const handleCreateJob = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy("job");
    setError("");
    resetOutputs();
    try {
      const job = await createJob({
        title: jobForm.title,
        company: jobForm.company || undefined,
        description: jobForm.description,
      });
      await refresh();
      setJobId(job.id);
      setJobForm(emptyJobForm);
      setNotice("Job description saved.");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not save the job.");
    } finally {
      setBusy("");
    }
  };

  const handleMatch = async () => {
    setBusy("match");
    setError("");
    setReport(null);
    setTailoredVersion(null);
    setCoverLetter(null);
    try {
      setReport(await scoreMatch(cvId, jobId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not score this CV against the job.");
    } finally {
      setBusy("");
    }
  };

  const handleTailor = async () => {
    setBusy("tailor");
    setError("");
    setTailoredVersion(null);
    try {
      setTailoredVersion(await tailorCV(cvId, jobId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not generate a tailored CV.");
    } finally {
      setBusy("");
    }
  };

  const handleCoverLetter = async () => {
    setBusy("cover");
    setError("");
    try {
      setCoverLetter(await generateCoverLetter(cvId, jobId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not generate a cover letter.");
    } finally {
      setBusy("");
    }
  };

  const checklist = [
    { label: "CV selected", done: Boolean(cvId) },
    { label: "Job description saved", done: Boolean(jobId) },
    { label: "Match score reviewed", done: Boolean(report) },
    { label: "Recommendations reviewed", done: recommendations.length > 0 },
    { label: "Tailored CV generated", done: Boolean(tailoredVersion) },
    { label: "Cover letter generated", done: Boolean(coverLetter) },
  ];

  const canScore = Boolean(cvId && jobId && selectedCv?.parse_status === "done");
  const canGenerate = Boolean(canScore && report);

  return (
    <div className="py-8 space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Application workflow</p>
          <h1 className="text-3xl font-bold text-gray-900">Build a targeted application</h1>
        </div>
        <div className="flex flex-wrap gap-2">
          {checklist.map((item) => (
            <span
              key={item.label}
              className={`text-xs px-2.5 py-1 rounded-full border ${
                item.done ? "bg-green-50 text-green-700 border-green-200" : "bg-white text-gray-500 border-gray-200"
              }`}
            >
              {item.done ? "Done" : "Todo"}: {item.label}
            </span>
          ))}
        </div>
      </div>

      {error && <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">{error}</p>}
      {notice && <p className="text-sm text-green-700 bg-green-50 border border-green-100 rounded-lg p-3">{notice}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5 space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-800">1. Choose or upload a CV</h2>
            <label className="cursor-pointer bg-blue-600 text-white text-sm font-medium px-3 py-2 rounded-md hover:bg-blue-700">
              {busy === "upload" ? "Uploading..." : "Upload"}
              <input ref={fileRef} type="file" accept=".pdf,.docx" className="hidden" onChange={handleUpload} />
            </label>
          </div>
          <select
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            value={cvId}
            onChange={(event) => {
              setCvId(event.target.value);
              resetOutputs();
            }}
          >
            <option value="">Select an existing CV</option>
            {cvs.map((cv) => (
              <option key={cv.id} value={cv.id}>
                {cv.filename} ({cv.parse_status})
              </option>
            ))}
          </select>
          {selectedCv && (
            <div className="text-sm text-gray-600 border-t border-gray-100 pt-3">
              <p className="font-medium text-gray-800">{selectedCv.filename}</p>
              <p>Status: {selectedCv.parse_status}</p>
              {selectedCv.parse_status !== "done" && (
                <p className="text-yellow-700 mt-1">This CV must parse successfully before scoring or tailoring.</p>
              )}
            </div>
          )}
        </section>

        <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5 space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">2. Choose or paste a job description</h2>
          <select
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            value={jobId}
            onChange={(event) => {
              setJobId(event.target.value);
              resetOutputs();
            }}
          >
            <option value="">Select an existing job</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title}{job.company ? ` - ${job.company}` : ""}
              </option>
            ))}
          </select>

          <form onSubmit={handleCreateJob} className="space-y-3 border-t border-gray-100 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                placeholder="Job title"
                value={jobForm.title}
                onChange={(event) => setJobForm({ ...jobForm, title: event.target.value })}
                required
              />
              <input
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                placeholder="Company"
                value={jobForm.company}
                onChange={(event) => setJobForm({ ...jobForm, company: event.target.value })}
              />
            </div>
            <textarea
              rows={7}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="Paste the job description here"
              value={jobForm.description}
              onChange={(event) => setJobForm({ ...jobForm, description: event.target.value })}
              required
            />
            <button
              type="submit"
              disabled={busy === "job"}
              className="bg-gray-900 text-white text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-800 disabled:opacity-50"
            >
              {busy === "job" ? "Saving..." : "Save job description"}
            </button>
          </form>
        </section>
      </div>

      <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5 space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">3. Score and review fit</h2>
            <p className="text-sm text-gray-500">Run the match before generating a tailored CV or cover letter.</p>
          </div>
          <button
            onClick={handleMatch}
            disabled={!canScore || busy === "match"}
            className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {busy === "match" ? "Scoring..." : "Get match score"}
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="border border-gray-100 rounded-lg p-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Job signals</p>
            <p className="text-xs text-gray-500 mb-3">Seniority: {jobInsights.seniority}</p>
            {["required", "niceToHave", "responsibilities"].map((key) => {
              const labels: Record<string, string> = {
                required: "Required",
                niceToHave: "Nice to have",
                responsibilities: "Responsibilities",
              };
              const values = jobInsights[key as keyof typeof jobInsights] as string[];
              return (
                <div key={key} className="mb-3 last:mb-0">
                  <p className="text-xs font-semibold text-gray-600 mb-1">{labels[key]}</p>
                  {values.length ? (
                    <ul className="space-y-1">
                      {values.map((value) => (
                        <li key={value} className="text-xs text-gray-500">{value}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-gray-400">No clear signals detected.</p>
                  )}
                </div>
              );
            })}
          </div>

          <div className="border border-gray-100 rounded-lg p-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Match result</p>
            {report ? (
              <>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-bold text-gray-900">{report.overall_score}%</span>
                  <span className={`text-lg font-semibold ${gradeColor[report.grade] ?? "text-gray-600"}`}>
                    {report.grade}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-2">{report.explanation}</p>
              </>
            ) : (
              <p className="text-sm text-gray-400">No score yet.</p>
            )}
          </div>

          <div className="border border-gray-100 rounded-lg p-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Recommended edits</p>
            {recommendations.length ? (
              <div className="space-y-2">
                {recommendations.map((item) => (
                  <div key={`${item.title}-${item.detail}`} className="border-l-2 border-blue-200 pl-3">
                    <p className="text-sm font-medium text-gray-800">{item.title}</p>
                    <p className="text-xs text-gray-500">{item.detail}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400">Run a match to see suggested changes.</p>
            )}
          </div>
        </div>
      </section>

      <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5 space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">Advanced coaching</h2>
            <p className="text-sm text-gray-500">Get more detailed suggestions for closing the strongest CV-to-job gaps.</p>
          </div>
          <button
            onClick={handleCoaching}
            disabled={!canScore || busy === "coaching"}
            className="bg-gray-900 text-white text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-800 disabled:opacity-50"
          >
            {busy === "coaching" ? "Analysing..." : "Get coaching tips"}
          </button>
        </div>

        {coaching ? (
          <div className="space-y-4">
            <div className="border border-gray-100 rounded-lg p-4">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold text-gray-900">{coaching.overall_score}%</span>
                <span className="text-sm font-semibold text-gray-500">{coaching.grade}</span>
              </div>
              <p className="text-sm text-gray-600 mt-2">{coaching.headline}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(coaching.tips ?? []).map((tip: any, index: number) => (
                <div key={`${tip.category}-${tip.gap}-${index}`} className="border border-gray-100 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${tip.priority === "high" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>
                      {tip.priority}
                    </span>
                    <span className="text-xs text-gray-400 capitalize">{tip.category}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-800">{tip.gap}</p>
                  <p className="text-sm text-gray-600 mt-1">{tip.tip}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-400">Run coaching after selecting a parsed CV and saved job.</p>
        )}
      </section>

      <section className="bg-white border border-gray-100 shadow-sm rounded-lg p-5 space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">4. Generate tailored documents</h2>
            <p className="text-sm text-gray-500">Review unsupported-claim warnings before exporting.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleTailor}
              disabled={!canGenerate || busy === "tailor"}
              className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {busy === "tailor" ? "Tailoring..." : "Generate improved CV"}
            </button>
            <button
              onClick={handleCoverLetter}
              disabled={!canGenerate || busy === "cover"}
              className="bg-gray-900 text-white text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-800 disabled:opacity-50"
            >
              {busy === "cover" ? "Writing..." : "Generate cover letter"}
            </button>
          </div>
        </div>

        {tailoredVersion && !tailoredVersion.validation_passed && (
          <p className="text-sm text-yellow-800 bg-yellow-50 border border-yellow-100 rounded-lg p-3">
            The tailored CV did not pass the current truth check. Review it carefully before using or exporting.
          </p>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="border border-gray-100 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-gray-700">Before / after comparison</p>
              {tailoredVersion && (
                <div className="flex gap-2">
                  <button onClick={() => downloadDocx(tailoredVersion.id)} className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-md">DOCX</button>
                  <button onClick={() => downloadPdf(tailoredVersion.id)} className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-md">PDF</button>
                </div>
              )}
            </div>
            {(["summary", "skills", "experience"] as const).map((section) => (
              <div key={section} className="grid grid-cols-1 md:grid-cols-2 gap-3 border-t border-gray-100 pt-3">
                <div>
                  <p className="text-xs font-semibold uppercase text-gray-400 mb-1">Original {section}</p>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">{sectionText(selectedCv?.parsed_data, section)}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase text-gray-400 mb-1">Tailored {section}</p>
                  <p className="text-sm text-gray-800 whitespace-pre-wrap">{sectionText(tailoredVersion?.tailored_data, section)}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="border border-gray-100 rounded-lg p-4">
            <div className="flex items-center justify-between gap-3 mb-3">
              <p className="text-sm font-semibold text-gray-700">Cover letter</p>
              {coverLetter && (
                <button
                  onClick={() => downloadCoverLetterText(coverLetter.content)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-md"
                >
                  TXT
                </button>
              )}
            </div>
            {coverLetter ? (
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                {coverLetter.content}
              </pre>
            ) : (
              <p className="text-sm text-gray-400">No cover letter generated yet.</p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default ApplicationBuilder;
