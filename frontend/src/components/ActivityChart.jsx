function ActivityChart({ isDarkMode, prediction, raiHistory }) {
  const width = 520;
  const height = 180;
  const padding = 18;
  const maxValue = Math.max(...raiHistory, 15);

  const points = raiHistory
    .map((value, index) => {
      const x = padding + (index * (width - padding * 2)) / Math.max(raiHistory.length - 1, 1);
      const y = height - padding - ((value / maxValue) * (height - padding * 2));
      return `${x},${y}`;
    })
    .join(" ");

  const panelClass = isDarkMode
    ? "border-emerald-800/60 bg-emerald-950/45 shadow-black/20"
    : "border-emerald-300/90 bg-white/84 shadow-emerald-900/10";
  const chartClass = isDarkMode
    ? "border-white/8 bg-black/20"
    : "border-emerald-300/90 bg-emerald-50/94";

  return (
    <section className={`rounded-[1.75rem] border p-6 shadow-xl ${panelClass}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className={`text-xs uppercase tracking-[0.25em] ${isDarkMode ? "text-emerald-200/55" : "text-emerald-900/55"}`}>Activity</p>
          <h2 className={`mt-3 text-2xl font-semibold ${isDarkMode ? "text-white" : "text-emerald-950"}`}>
            RAI: {prediction?.rai ?? "--"} detections/min
          </h2>
          <p className={`mt-2 text-sm ${isDarkMode ? "text-emerald-50/65" : "text-emerald-950/72"}`}>
            Rolling detection trend
          </p>
        </div>
      </div>

      <div className={`mt-6 rounded-3xl border p-4 ${chartClass}`}>
        <svg viewBox={`0 0 ${width} ${height}`} className="h-60 w-full xl:h-72">
          {[0.25, 0.5, 0.75].map((marker) => {
            const y = height - padding - marker * (height - padding * 2);
            return (
              <line
                key={marker}
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke={isDarkMode ? "rgba(255,255,255,0.08)" : "rgba(6,95,70,0.12)"}
                strokeDasharray="4 6"
              />
            );
          })}

          <polyline
            fill="none"
            stroke="#6ee7b7"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={points}
          />

          {raiHistory.map((value, index) => {
            const x = padding + (index * (width - padding * 2)) / Math.max(raiHistory.length - 1, 1);
            const y = height - padding - ((value / maxValue) * (height - padding * 2));

            return (
              <g key={`${value}-${index}`}>
                <circle cx={x} cy={y} r="5" fill="#d1fae5" />
                <text
                  x={x}
                  y={y - 12}
                  textAnchor="middle"
                  fill={isDarkMode ? "#d1fae5" : "#065f46"}
                  fontSize="11"
                >
                  {value}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </section>
  );
}

export default ActivityChart;
