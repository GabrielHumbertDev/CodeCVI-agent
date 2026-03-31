import client from "./client";

export const tailorCV = (cv_id: string, job_id: string) =>
  client.post("/tailor", { cv_id, job_id }).then((r) => r.data);

export const listVersions = (cv_id: string) =>
  client.get(`/tailor/${cv_id}/versions`).then((r) => r.data);
