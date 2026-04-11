function AlertBanner({ isDarkMode, prediction, systemAlert }) {
  if (!prediction?.rare && !systemAlert) {
    return (
      <section className={`rounded-[1.75rem] border p-5 shadow-xl ${isDarkMode ? "border-emerald-800/60 bg-emerald-950/45 shadow-black/20" : "border-emerald-300/90 bg-white/84 shadow-emerald-900/10"}`}>
        <div className="flex items-center gap-3">
          <span className="h-3 w-3 rounded-full bg-lime-400 shadow-[0_0_12px_rgba(163,230,53,0.7)]" />
          <p className={`text-sm font-medium ${isDarkMode ? "text-emerald-50/80" : "text-emerald-900"}`}>
            Alert channel clear
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className={`rounded-[1.75rem] border p-5 shadow-[0_0_40px_rgba(245,158,11,0.1)] ${
      isDarkMode
        ? "border-amber-500/30 bg-amber-500/10"
        : "border-amber-500/60 bg-amber-50"
    }`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          {prediction?.rare ? (
            <p className={`text-base font-semibold ${isDarkMode ? "text-amber-100" : "text-amber-900"}`}>
              Rare species detected: {prediction.species}
            </p>
          ) : null}
          {systemAlert ? (
            <p className={`text-sm ${isDarkMode ? "text-amber-50/85" : "text-amber-800"}`}>{systemAlert}</p>
          ) : null}
        </div>
        <span className={`inline-flex w-fit rounded-full border px-3 py-1 text-xs uppercase tracking-[0.22em] ${
          isDarkMode
            ? "border-amber-300/25 bg-black/20 text-amber-100"
            : "border-amber-500/50 bg-amber-100 text-amber-900"
        }`}>
          Priority Alert
        </span>
      </div>
    </section>
  );
}

export default AlertBanner;
