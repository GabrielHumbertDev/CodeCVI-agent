import client from "./client";

export const searchJobsForCV = (cv_id: string, top_k = 5) =>
  client.post("/search/jobs-for-cv", { cv_id, top_k }).then((r) => r.data);

export const searchCVsForJob = (job_id: string, top_k = 5) =>
  client.post("/search/cvs-for-job", { job_id, top_k }).then((r) => r.data);
