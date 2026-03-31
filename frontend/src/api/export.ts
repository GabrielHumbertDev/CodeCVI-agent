import client from "./client";

export const downloadDocx = async (version_id: string) => {
  const res = await client.get(`/export/versions/${version_id}/docx`, { responseType: "blob" });
  const url = URL.createObjectURL(res.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = `cv_${version_id}.docx`;
  a.click();
  URL.revokeObjectURL(url);
};

export const downloadPdf = async (version_id: string) => {
  const res = await client.get(`/export/versions/${version_id}/pdf`, { responseType: "blob" });
  const url = URL.createObjectURL(res.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = `cv_${version_id}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
};
