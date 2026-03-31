import { useEffect, useState } from "react";
import { getDashboard } from "../api/analytics";

const gradeColor: Record<string, string> = {
  Excellent: "text-green-600",
  Good: "text-blue-600",
  Fair: "text-yellow-600",
  Poor: "text-red-600",
};

const Dashboard = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => setError("Failed to load dashboard."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="py-10 text-gray-500">Loading...</p>;
  if (error) return <p className="py-10 text-red-500">{error}</p>;

  const { totals, applications_last_30_days, status_breakdown, match_scores, best_performing_version } = data;

  return (
    <div className="py-10 space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>

      {/* Totals */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "CVs", value: totals.cvs },
          { label: "Jobs", value: totals.jobs },
          { label: "Applications", value: totals.applications },
          { label: "CV Versions", value: totals.cv_versions },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
            <p className="text-sm text-gray-500">{item.label}</p>
            <p className="text-3xl font-bold text-gray-800 mt-1">{item.value}</p>
          </div>
        ))}
      </div>

      {/* Match score + activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <p className="text-sm text-gray-500 mb-1">Average Match Score</p>
          {match_scores.average !== null ? (
            <>
              <p className="text-4xl font-bold text-gray-800">{match_scores.average}%</p>
              <p className={`text-sm font-medium mt-1 ${gradeColor[match_scores.grade] ?? "text-gray-600"}`}>
                {match_scores.grade} · {match_scores.count} version{match_scores.count !== 1 ? "s" : ""} scored
              </p>
            </>
          ) : (
            <p className="text-gray-400 mt-2">No versions scored yet</p>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <p className="text-sm text-gray-500 mb-1">Applications (last 30 days)</p>
          <p className="text-4xl font-bold text-gray-800">{applications_last_30_days}</p>
          {Object.keys(status_breakdown).length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {Object.entries(status_breakdown).map(([status, count]) => (
                <span key={status} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                  {status}: {count as number}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Best version */}
      {best_performing_version && (
        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <p className="text-sm text-gray-500 mb-2">Best Performing CV Version</p>
          <p className="font-semibold text-gray-800">{best_performing_version.cv_filename}</p>
          <p className="text-sm text-gray-500">
            {best_performing_version.job_title} ·{" "}
            <span className={`font-medium ${gradeColor[best_performing_version.grade] ?? ""}`}>
              {best_performing_version.score}% ({best_performing_version.grade})
            </span>
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
