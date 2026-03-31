import client from "./client";

export const exportMyData = () =>
  client.get("/gdpr/export").then((r) => r.data);

export const getAuditLog = () =>
  client.get("/gdpr/audit-log").then((r) => r.data);

export const updateConsent = (consent: boolean) =>
  client.post("/gdpr/consent", { consent }).then((r) => r.data);

export const deleteMyAccount = (password: string) =>
  client.delete("/gdpr/me", { data: { password, confirm: "DELETE MY ACCOUNT" } }).then((r) => r.data);
