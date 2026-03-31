import client from "./client";

export const login = (email: string, password: string) =>
  client.post("/auth/login", { email, password }).then((r) => r.data);

export const register = (email: string, password: string, full_name: string) =>
  client.post("/auth/register", { email, password, full_name }).then((r) => r.data);

export const getMe = () => client.get("/auth/me").then((r) => r.data);
