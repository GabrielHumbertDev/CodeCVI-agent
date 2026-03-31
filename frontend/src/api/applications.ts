import client from "./client";

export const createApplication = (data: { job_id: string; cv_version_id?: string; notes?: string }) =>
  client.post("/applications", data).then((r) => r.data);

export const listApplications = () =>
  client.get("/applications").then((r) => r.data);

export const updateApplication = (id: string, data: { status?: string; notes?: string }) =>
  client.put(`/applications/${id}`, data).then((r) => r.data);

export const deleteApplication = (id: string) =>
  client.delete(`/applications/${id}`);

export const getReadiness = (id: string) =>
  client.get(`/applications/${id}/readiness`).then((r) => r.data);
