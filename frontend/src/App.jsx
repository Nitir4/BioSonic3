import { useEffect, useState } from "react";
import ActivityChart from "./components/ActivityChart";
import AlertBanner from "./components/AlertBanner";
import HotspotMap from "./components/HotspotMap";
import InputSection from "./components/InputSection";
import PredictionCard from "./components/PredictionCard";

const speciesList = ["Tiger", "Elephant", "Deer", "Hornbill", "Leopard"];
const rareSpecies = ["Tiger", "Leopard"];

const routePool = [
  ["A", "B", "C"],
  ["A", "C", "B"],
  ["B", "A", "C"],
  ["C", "B", "A"],
];

const incidentPool = ["", "", "Gunshot pattern flagged", "Chainsaw audio signature"];

const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [lastFileName, setLastFileName] = useState("—");
  const [prediction, setPrediction] = useState(null);
  const [raiHistory, setRaiHistory] = useState([4, 6, 5, 8, 7, 9, 11]);
  const [zoneActivity, setZoneActivity] = useState([
    { name: "Zone A", value: 7 },
    { name: "Zone B", value: 11 },
    { name: "Zone C", value: 5 },
  ]);
  const [movementPath, setMovementPath] = useState(["A", "B", "C"]);
  const [systemAlert, setSystemAlert] = useState("");

  // ── Simulation fallback (used when no backend or backend errors) ────────────
  const runSimulation = (fileName) => {
    const species = speciesList[randomInt(0, speciesList.length - 1)];
    const confidence = randomInt(70, 98);
    const rai = randomInt(2, 15);
    const zones = ["Zone A", "Zone B", "Zone C"].map((zone) => ({
      name: zone,
      value: randomInt(3, 15),
    }));

    if (fileName) setLastFileName(fileName);
    setPrediction({
      species,
      confidence,
      rai,
      rare: rareSpecies.includes(species),
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    });
    setRaiHistory((prev) => [...prev.slice(-7), rai]);
    setZoneActivity(zones);
    setMovementPath(routePool[randomInt(0, routePool.length - 1)]);
    setSystemAlert(incidentPool[randomInt(0, incidentPool.length - 1)]);
  };

  // ── Real backend result handler ───────────────────────────────────────────
  // Backend response shape:
  //   { species, confidence, rai, zones: {A, B, C}, movement }
  const handleRealResult = (fileName, data) => {
    if (fileName) setLastFileName(fileName);

    const confidencePct = Math.round((data.confidence ?? 0) * 100);
    const species = data.species ?? "Unknown";
    const rai = data.rai ?? 0;

    setPrediction({
      species,
      confidence: confidencePct,
      rai,
      rare: rareSpecies.includes(species),
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    });

    setRaiHistory((prev) => [...prev.slice(-7), rai]);

    // Map { A, B, C } counts from backend → [{ name, value }, …]
    const zones = data.zones
      ? Object.entries(data.zones).map(([key, val]) => ({
          name: `Zone ${key}`,
          value: val,
        }))
      : zoneActivity;
    setZoneActivity(zones);

    // Parse movement string "A → B → C" into array ["A","B","C"]
    const rawMovement = data.movement ?? "";
    const parsedPath = rawMovement
      .split("→")
      .map((s) => s.trim())
      .filter(Boolean);
    setMovementPath(parsedPath.length ? parsedPath : ["A", "B", "C"]);

    setSystemAlert(incidentPool[randomInt(0, incidentPool.length - 1)]);
  };

  useEffect(() => {
    runSimulation(null);
  }, []);

  useEffect(() => {
    if (!prediction) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      setZoneActivity((current) =>
        current.map((zone) => ({
          ...zone,
          value: Math.max(2, Math.min(15, zone.value + randomInt(-2, 2))),
        })),
      );
    }, 4000);

    return () => window.clearInterval(intervalId);
  }, [prediction]);

  const shellClass = isDarkMode
    ? "bg-[radial-gradient(circle_at_top,rgba(38,92,64,0.35),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(245,158,11,0.12),transparent_22%),linear-gradient(180deg,#06110a_0%,#0a1710_45%,#08120c_100%)] text-stone-100"
    : "bg-[radial-gradient(circle_at_top,rgba(74,222,128,0.22),transparent_24%),linear-gradient(180deg,#edf8f0_0%,#e4f1e6_48%,#d8eadb_100%)] text-emerald-950";

  const heroClass = isDarkMode
    ? "border-emerald-800/60 bg-emerald-950/55"
    : "border-emerald-300/90 bg-white/84";

  const chipClass = isDarkMode
    ? "border-emerald-400/20 bg-emerald-300/10 text-emerald-200/80"
    : "border-emerald-300/80 bg-emerald-100 text-emerald-950";

  const infoCardClass = isDarkMode
    ? "border-white/8 bg-black/20"
    : "border-emerald-300/90 bg-white/88";

  const mutedTextClass = isDarkMode ? "text-emerald-50/70" : "text-emerald-950/72";
  const labelTextClass = isDarkMode ? "text-emerald-200/55" : "text-emerald-950/62";
  const headingClass = isDarkMode ? "text-white" : "text-emerald-950";

  return (
    <main className={`${shellClass} flex h-screen flex-col overflow-hidden px-3 py-3 transition-colors duration-300 sm:px-4 sm:py-4 lg:px-5 lg:py-5`}>
      <div className="flex h-full w-full flex-col gap-5">
        <section className={`relative overflow-hidden rounded-[2rem] border p-5 shadow-[0_30px_80px_rgba(0,0,0,0.18)] backdrop-blur ${heroClass}`}>
          <div className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent ${isDarkMode ? "via-emerald-300/60" : "via-emerald-700/35"} to-transparent`} />
          <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-4">
              {/* BioSonic waveform symbol */}
              <svg viewBox="0 0 36 36" className="h-9 w-9 shrink-0" fill="none" aria-hidden="true">
                <rect x="2" y="14" width="4" height="8" rx="2" fill={isDarkMode ? "#6ee7b7" : "#059669"} />
                <rect x="8" y="8" width="4" height="20" rx="2" fill={isDarkMode ? "#6ee7b7" : "#059669"} />
                <rect x="14" y="4" width="4" height="28" rx="2" fill={isDarkMode ? "#34d399" : "#047857"} />
                <rect x="20" y="8" width="4" height="20" rx="2" fill={isDarkMode ? "#6ee7b7" : "#059669"} />
                <rect x="26" y="14" width="4" height="8" rx="2" fill={isDarkMode ? "#6ee7b7" : "#059669"} />
                <rect x="32" y="16" width="2" height="4" rx="1" fill={isDarkMode ? "#a7f3d0" : "#047857"} opacity="0.6" />
              </svg>
              <div className="space-y-1">
                <span className={`inline-flex items-center rounded-full border px-3 py-0.5 text-xs uppercase tracking-[0.35em] ${chipClass}`}>
                  Field Monitor
                </span>
                <h1 className={`text-2xl font-semibold tracking-tight sm:text-3xl ${headingClass}`}>
                  BioSonic Wildlife Command Dashboard
                </h1>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <button
                type="button"
                onClick={() => setIsDarkMode((current) => !current)}
                className={`rounded-2xl border px-4 py-3 text-left transition hover:scale-[1.01] ${infoCardClass}`}
                aria-label="Toggle theme"
              >
                <p className={`text-xs uppercase tracking-[0.25em] ${labelTextClass}`}>
                  Theme
                </p>
                <div className="mt-2 flex items-center gap-2">
                  {/* Waveform icon used as theme indicator */}
                  <svg viewBox="0 0 20 20" className="h-4 w-4 shrink-0" fill="none" aria-hidden="true">
                    <rect x="1" y="7" width="2" height="6" rx="1" fill={isDarkMode ? "#d1fae5" : "#059669"} />
                    <rect x="5" y="4" width="2" height="12" rx="1" fill={isDarkMode ? "#d1fae5" : "#059669"} />
                    <rect x="9" y="1" width="2" height="18" rx="1" fill={isDarkMode ? "#6ee7b7" : "#047857"} />
                    <rect x="13" y="4" width="2" height="12" rx="1" fill={isDarkMode ? "#d1fae5" : "#059669"} />
                    <rect x="17" y="7" width="2" height="6" rx="1" fill={isDarkMode ? "#d1fae5" : "#059669"} />
                  </svg>
                  <span className={`text-sm font-medium ${headingClass}`}>{isDarkMode ? "Dark" : "Light"}</span>
                </div>
              </button>
              <div className={`rounded-2xl border px-4 py-3 ${infoCardClass}`}>
                <p className={`text-xs uppercase tracking-[0.25em] ${labelTextClass}`}>
                  System Status
                </p>
                <div className={`mt-2 flex items-center gap-2 text-sm font-medium ${headingClass}`}>
                  <span className="h-2.5 w-2.5 rounded-full bg-lime-400 shadow-[0_0_16px_rgba(163,230,53,0.8)]" />
                  Active
                </div>
              </div>
              <div className={`rounded-2xl border px-4 py-3 ${infoCardClass}`}>
                <p className={`text-xs uppercase tracking-[0.25em] ${labelTextClass}`}>
                  Last File
                </p>
                <p className={`mt-2 truncate text-sm font-medium ${headingClass}`} title={lastFileName}>
                  {lastFileName}
                </p>
              </div>
            </div>
          </div>

          <InputSection
            isDarkMode={isDarkMode}
            onResult={handleRealResult}
            onSimulate={runSimulation}
          />
        </section>

        <section className="grid min-h-0 flex-1 gap-5 2xl:grid-cols-[1.4fr_1fr]">
          <div className="flex min-h-0 flex-col gap-5 overflow-auto">
            <AlertBanner
              isDarkMode={isDarkMode}
              prediction={prediction}
              systemAlert={systemAlert}
            />
            <PredictionCard isDarkMode={isDarkMode} prediction={prediction} />
            <ActivityChart
              isDarkMode={isDarkMode}
              prediction={prediction}
              raiHistory={raiHistory}
            />
          </div>

          <div className="min-h-0">
            <HotspotMap
              isDarkMode={isDarkMode}
              movementPath={movementPath}
              zoneActivity={zoneActivity}
            />
          </div>
        </section>
      </div>
    </main>
  );
}

export default App;
