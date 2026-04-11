function HotspotMap({ isDarkMode, movementPath, zoneActivity }) {
  const positions = [
    "self-start justify-self-start",
    "self-center justify-self-center",
    "self-end justify-self-end",
  ];

  const panelClass = isDarkMode
    ? "border-emerald-800/60 bg-emerald-950/45 shadow-black/20"
    : "border-emerald-300/90 bg-white/84 shadow-emerald-900/10";

  const mapClass = isDarkMode
    ? "border-white/8 bg-[radial-gradient(circle_at_top,rgba(74,222,128,0.12),transparent_35%),linear-gradient(180deg,rgba(4,14,8,0.95),rgba(7,24,14,0.95))]"
    : "border-emerald-300/90 bg-[radial-gradient(circle_at_top,rgba(16,185,129,0.18),transparent_35%),linear-gradient(180deg,rgba(252,255,253,0.98),rgba(232,247,238,0.98))]";

  return (
    <section className={`flex h-full flex-col rounded-[1.75rem] border p-6 shadow-xl ${panelClass}`}>
      <p className={`text-xs uppercase tracking-[0.25em] ${isDarkMode ? "text-emerald-200/55" : "text-emerald-900/70"}`}>Zones</p>
      <div className="mt-3 flex items-end justify-between gap-3">
        <div>
          <h2 className={`text-2xl font-semibold ${isDarkMode ? "text-white" : "text-emerald-950"}`}>Zone Activity</h2>
          <p className={`mt-1 text-sm ${isDarkMode ? "text-emerald-50/60" : "text-emerald-950/65"}`}>
            Relative detection buckets, not a GPS-backed map.
          </p>
        </div>
        <div className={`rounded-full border px-3 py-1 text-xs uppercase tracking-[0.2em] ${isDarkMode ? "border-emerald-400/20 bg-emerald-300/10 text-emerald-100" : "border-emerald-400 bg-emerald-50 text-emerald-900"}`}>
          Route {movementPath.join(" → ")}
        </div>
      </div>

      <div className={`mt-6 flex-1 grid grid-cols-3 rounded-[1.75rem] border p-5 ${mapClass}`}>
        {zoneActivity.map((zone, index) => (
          <div key={zone.name} className={`flex ${positions[index]}`}>
            <div
              className={`flex flex-col items-center justify-center rounded-full border text-center shadow-[0_0_30px_rgba(16,185,129,0.18)] ${
                isDarkMode
                  ? "border-emerald-300/20 bg-emerald-400/10"
                  : "border-emerald-400/80 bg-emerald-100/94"
              }`}
              style={{
                width: `${zone.value * 12}px`,
                height: `${zone.value * 12}px`,
                minWidth: "98px",
                minHeight: "98px",
              }}
            >
              <span className={`text-xs uppercase tracking-[0.2em] ${isDarkMode ? "text-emerald-100/70" : "text-emerald-900/80"}`}>
                {zone.name}
              </span>
              <span className={`mt-1 text-lg font-semibold ${isDarkMode ? "text-white" : "text-emerald-950"}`}>
                {zone.value}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {movementPath.map((zone, index) => (
          <div
            key={`${zone}-${index}`}
            className={`rounded-2xl border px-4 py-3 ${isDarkMode ? "border-white/8 bg-black/20" : "border-emerald-300/90 bg-emerald-50/95"}`}
          >
            <p className={`text-xs uppercase tracking-[0.2em] ${isDarkMode ? "text-emerald-100/60" : "text-emerald-900/70"}`}>
              {index === 0 ? "Origin" : index === movementPath.length - 1 ? "Exit" : "Transit"}
            </p>
            <p className={`mt-2 text-lg font-semibold ${isDarkMode ? "text-white" : "text-emerald-950"}`}>
              Zone {zone}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default HotspotMap;
