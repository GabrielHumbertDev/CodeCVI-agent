import client from "./client";

export const listUsers = (params?: {
  status?: string;
  role?: string;
  search?: string;
  include_deleted?: boolean;
}) => client.get("/admin/users", { params }).then((r) => r.data);

export const getUser = (id: string) =>
  client.get(`/admin/users/${id}`).then((r) => r.data);

export const editUser = (id: string, data: { full_name?: string; email?: string; role?: string }) =>
  client.put(`/admin/users/${id}`, data).then((r) => r.data);

export const approveUser = (id: string) =>
  client.post(`/admin/users/${id}/approve`).then((r) => r.data);

export const pauseUser = (id: string, reason?: string) =>
  client.post(`/admin/users/${id}/pause`, { reason }).then((r) => r.data);

export const resumeUser = (id: string) =>
  client.post(`/admin/users/${id}/resume`).then((r) => r.data);

export const disableUser = (id: string) =>
  client.post(`/admin/users/${id}/disable`).then((r) => r.data);

export const deleteUser = (id: string) =>
  client.delete(`/admin/users/${id}`).then((r) => r.data);
