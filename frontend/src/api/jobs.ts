import client from "./client";

export const createJob = (data: { title: string; company?: string; description: string }) =>
  client.post("/jobs", data).then((r) => r.data);

export const listJobs = () => client.get("/jobs").then((r) => r.data);

export const deleteJob = (id: string) => client.delete(`/jobs/${id}`);
