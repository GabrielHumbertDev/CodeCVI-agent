import client from "./client";

export const scoreMatch = (cv_id: string, job_id: string) =>
  client.post("/match", { cv_id, job_id }).then((r) => r.data);
