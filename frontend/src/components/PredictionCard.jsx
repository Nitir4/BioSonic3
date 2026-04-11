function PredictionCard({ isDarkMode, prediction }) {
  if (!prediction) {
    return null;
  }

  const panelClass = isDarkMode
    ? "border-emerald-800/60 bg-emerald-950/45 shadow-black/20"
    : "border-emerald-300/90 bg-white/84 shadow-emerald-900/10";
  const metricClass = isDarkMode
    ? "border-white/8 bg-black/20"
    : "border-emerald-300/90 bg-emerald-50/95";

  return (
    <section className={`rounded-[1.75rem] border p-6 shadow-xl ${panelClass}`}>
      <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className={`text-xs uppercase tracking-[0.25em] ${isDarkMode ? "text-emerald-200/55" : "text-emerald-900/55"}`}>
            Prediction
          </p>
          <h2 className={`mt-3 text-3xl font-semibold ${isDarkMode ? "text-white" : "text-emerald-950"}`}>{prediction.species}</h2>
          <p className={`mt-2 text-sm ${isDarkMode ? "text-emerald-50/65" : "text-emerald-950/72"}`}>Updated {prediction.timestamp}</p>
        </div>

        <div className="grid gap-3 sm:min-w-64 sm:grid-cols-2">
          <div className={`rounded-2xl border p-4 ${metricClass}`}>
            <p className={`text-xs uppercase tracking-[0.2em] ${isDarkMode ? "text-stone-300/60" : "text-emerald-900/55"}`}>
              Confidence
            </p>
            <p className={`mt-2 text-2xl font-semibold ${isDarkMode ? "text-emerald-100" : "text-emerald-950"}`}>
              {prediction.confidence}%
            </p>
          </div>
          <div className={`rounded-2xl border p-4 ${metricClass}`}>
            <p className={`text-xs uppercase tracking-[0.2em] ${isDarkMode ? "text-stone-300/60" : "text-emerald-900/55"}`}>
              RAI
            </p>
            <p className={`mt-2 text-lg font-medium ${isDarkMode ? "text-white" : "text-emerald-950"}`}>
              {prediction.rai}/min
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default PredictionCard;
