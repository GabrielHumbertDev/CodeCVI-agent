import client from "./client";

export const uploadCV = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return client.post("/cvs/upload", form).then((r) => r.data);
};

export const listCVs = () => client.get("/cvs").then((r) => r.data);

export const deleteCV = (id: string) => client.delete(`/cvs/${id}`);
