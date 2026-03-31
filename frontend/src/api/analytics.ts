import client from "./client";

export const getDashboard = () =>
  client.get("/analytics/dashboard").then((r) => r.data);

export const getFunnel = () =>
  client.get("/analytics/funnel").then((r) => r.data);

export const getScoreTrend = (cv_id: string) =>
  client.get(`/analytics/score-trend/${cv_id}`).then((r) => r.data);

export const getCoaching = (cv_id: string, job_id: string) =>
  client.post("/analytics/coaching", { cv_id, job_id }).then((r) => r.data);
