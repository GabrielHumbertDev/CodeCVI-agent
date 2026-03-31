import { useEffect, useRef, useState } from "react";
import { uploadCV, listCVs, deleteCV } from "../api/cvs";

const CVs = () => {
  const [cvs, setCVs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const load = () =>
    listCVs()
      .then((d) => setCVs(d.cvs))
      .catch(() => setError("Failed to load CVs."))
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await uploadCV(file);
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this CV?")) return;
    try {
      await deleteCV(id);
      setCVs((prev) => prev.filter((c) => c.id !== id));
    } catch {
      setError("Delete failed.");
    }
  };

  const statusBadge = (s: string) => {
    const colors: Record<string, string> = {
      done: "bg-green-100 text-green-700",
      failed: "bg-red-100 text-red-700",
      pending: "bg-yellow-100 text-yellow-700",
    };
    return (
      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[s] ?? "bg-gray-100 text-gray-600"}`}>
        {s}
      </span>
    );
  };

  return (
    <div className="py-10 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">My CVs</h1>
        <label className="cursor-pointer bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700">
          {uploading ? "Uploading..." : "+ Upload CV"}
          <input ref={fileRef} type="file" accept=".pdf,.docx" className="hidden" onChange={handleUpload} />
        </label>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : cvs.length === 0 ? (
        <p className="text-gray-400">No CVs uploaded yet.</p>
      ) : (
        <div className="space-y-3">
          {cvs.map((cv) => (
            <div key={cv.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-800">{cv.filename}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {cv.file_type.toUpperCase()} · {new Date(cv.created_at).toLocaleDateString()} · {statusBadge(cv.parse_status)}
                </p>
              </div>
              <button
                onClick={() => handleDelete(cv.id)}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CVs;
