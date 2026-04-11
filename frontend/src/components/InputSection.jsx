import { useRef, useState } from "react";

// Backend URL — defaults to empty string for same-origin relative calls
const API_URL = import.meta.env.VITE_API_URL || "";

function InputSection({ isDarkMode, onResult, onSimulate }) {
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const panelClass = isDarkMode
    ? "border-emerald-700/40 bg-black/20"
    : "border-emerald-300/90 bg-white/84";
  const labelClass = isDarkMode ? "text-emerald-100/60" : "text-emerald-950/62";
  const subtextClass = isDarkMode ? "text-emerald-50/75" : "text-emerald-950/72";
  const inputClass = isDarkMode
    ? "border-dashed border-emerald-500/30 bg-black/20 text-emerald-50"
    : "border-dashed border-emerald-400 bg-white text-emerald-950";

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setError("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Call the backend (relative to current origin if API_URL is empty)
      const res = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      onResult(file.name, data);
    } catch (err) {
      console.error("Backend Error:", err);
      setError(err.message);
      // Fall back to simulation only ON ERROR so the UI stays usable
      onSimulate(file.name);
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr]">
      <div className={`rounded-3xl border p-5 ${panelClass}`}>
        <p className={`text-xs uppercase tracking-[0.28em] ${labelClass}`}>Audio Intake</p>
        <h2 className={`mt-3 text-xl font-semibold ${isDarkMode ? "text-white" : "text-emerald-950"}`}>
          Upload audio for analysis
        </h2>
        <p className={`mt-2 text-sm ${subtextClass}`}>
          Triggers live prediction, RAI, and zone refresh.
        </p>
        {error && (
          <p className="mt-2 text-xs text-amber-400">
            ⚠ Connection error: {error} — showing simulated data.
          </p>
        )}
      </div>

      <label className={`rounded-3xl border p-5 ${panelClass} ${loading ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}`}>
        <span className={`text-xs uppercase tracking-[0.25em] ${labelClass}`}>
          Upload Audio
        </span>
        <input
          ref={inputRef}
          type="file"
          accept="audio/*"
          disabled={loading}
          onChange={handleFileUpload}
          className={`mt-3 block w-full cursor-pointer rounded-xl border px-3 py-3 text-sm file:mr-3 file:rounded-full file:border-0 file:bg-emerald-300 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-emerald-950 disabled:cursor-not-allowed ${inputClass}`}
        />
        <p className={`mt-3 text-sm ${subtextClass}`}>
          {loading
            ? "⏳ Analysing audio…"
            : fileName
            ? `Loaded: ${fileName}`
            : "No file selected"}
        </p>
      </label>
    </div>
  );
}

export default InputSection;
