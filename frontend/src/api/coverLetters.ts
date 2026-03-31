import client from "./client";

export const generateCoverLetter = (cv_id: string, job_id: string) =>
  client.post("/cover-letters", { cv_id, job_id }).then((r) => r.data);

export const listCoverLettersByJob = (job_id: string) =>
  client.get(`/cover-letters/job/${job_id}`).then((r) => r.data);
