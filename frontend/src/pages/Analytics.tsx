import { useEffect, useState } from "react";
import { listCVs } from "../api/cvs";
import { getFunnel, getScoreTrend } from "../api/analytics";

const Analytics = () => {
  const [funnel, setFunnel] = useState<any>(null);
  const [cvs, setCVs] = useState<any[]>([]);
  const [cvId, setCvId] = useState("");
  const [trend, setTrend] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFunnel().then(setFunnel).finally(() => setLoading(false));
    listCVs().then((d) => setCVs(d.cvs));
  }, []);

  const handleTrend = async (id: string) => {
    setCvId(id);
    if (id) {
      const data = await getScoreTrend(id);
      setTrend(data);
    } else {
      setTrend(null);
    }
  };

  return (
    <div className="py-10 space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Analytics</h1>

      {/* Funnel */}
      {loading ? <p className="text-gray-400">Loading...</p> : funnel && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Application Funnel</h2>
          <div className="space-y-2">
            {funnel.funnel.map((bucket: any) => {
              const pct = funnel.total_applications > 0
                ? Math.round(bucket.count / funnel.total_applications * 100) : 0;
              return (
                <div key={bucket.status}>
                  <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                    <span className="capitalize">{bucket.status}</span>
                    <span>{bucket.count} ({pct}%)</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="h-3 bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-4 flex gap-6 text-sm text-gray-500">
            <span>Application rate: <strong>{funnel.conversion_rates.application_rate}%</strong></span>
            <span>Interview rate: <strong>{funnel.conversion_rates.interview_rate}%</strong></span>
            <span>Offer rate: <strong>{funnel.conversion_rates.offer_rate}%</strong></span>
          </div>
        </div>
      )}

      {/* Score trend */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
        <h2 className="text-sm font-semibold text-gray-700">Score Trend by CV</h2>
        <select
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          value={cvId}
          onChange={(e) => handleTrend(e.target.value)}
        >
          <option value="">-- select a CV --</option>
          {cvs.map((c) => <option key={c.id} value={c.id}>{c.filename}</option>)}
        </select>

        {trend && (
          trend.trend.length === 0 ? (
            <p className="text-gray-400 text-sm">No tailored versions yet for this CV.</p>
          ) : (
            <div className="space-y-2">
              {trend.score_delta != null && (
                <p className="text-sm text-gray-600">
                  Overall improvement:{" "}
                  <span className={trend.score_delta >= 0 ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
                    {trend.score_delta >= 0 ? "+" : ""}{trend.score_delta}%
                  </span>
                </p>
              )}
              {trend.trend.map((point: any) => (
                <div key={point.cv_version_id} className="flex items-center gap-3">
                  <span className="text-xs text-gray-400 w-16">v{point.version_number}</span>
                  <div className="flex-1 bg-gray-100 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${point.score >= 60 ? "bg-green-500" : point.score >= 40 ? "bg-yellow-400" : "bg-red-400"}`}
                      style={{ width: `${point.score}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-gray-700 w-16">{point.score}% {point.grade}</span>
                  <span className="text-xs text-gray-400 hidden md:block">{point.job_title}</span>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default Analytics;
