import React, { useState, useRef } from "react";
import { detectAudio } from "../api";

const PRIMARY = "#193ce6";
const BG = "#f6f6f8";
const BORDER = "#e2e4ed";
const NEUTRAL = "#eef0f7";

const s = {
  root: { backgroundColor: BG, color: "#0f172a", fontFamily: "'Inter', sans-serif", minHeight: "100vh" },
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: `1px solid ${BORDER}`, backgroundColor: "white", padding: "0.75rem 2.5rem" },
  logoRow: { display: "flex", alignItems: "center", gap: 12 },
  logoIcon: { width: 32, height: 32, backgroundColor: PRIMARY, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", color: "white" },
  logoText: { fontSize: "1.125rem", fontWeight: 700, color: "#0f172a", margin: 0 },
  nav: { display: "flex", gap: "1.5rem" },
  navLink: { fontSize: "0.875rem", fontWeight: 500, color: "#475569", background: "none", border: "none", cursor: "pointer", padding: "0.25rem 0" },
  navLinkActive: { fontSize: "0.875rem", fontWeight: 700, color: PRIMARY, background: "none", borderBottom: `2px solid ${PRIMARY}`, border: "none", cursor: "pointer", padding: "0.25rem 0 0.5rem" },
  main: { maxWidth: "64rem", margin: "0 auto", padding: "2.5rem", display: "flex", flexDirection: "column", gap: "2rem" },
  pageTitle: { fontSize: "1.875rem", fontWeight: 800, letterSpacing: "-0.025em", color: "#0f172a", margin: 0 },
  pageSub: { fontSize: "1.125rem", color: "#64748b", margin: "0.25rem 0 0" },
  card: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, boxShadow: "0 1px 3px rgba(0,0,0,0.04)" },
  uploadCard: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px dashed ${BORDER}`, padding: "3rem 2rem", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", gap: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.04)", cursor: "pointer" },
  uploadIcon: { width: 64, height: 64, borderRadius: "50%", backgroundColor: `${PRIMARY}0D`, display: "flex", alignItems: "center", justifyContent: "center", color: PRIMARY },
  btnPrimary: { backgroundColor: PRIMARY, color: "white", fontWeight: 700, padding: "0.75rem 2rem", borderRadius: "0.5rem", border: "none", cursor: "pointer", boxShadow: `0 4px 12px ${PRIMARY}33`, fontSize: "0.875rem" },
  btnPrimaryLg: { backgroundColor: PRIMARY, color: "white", fontWeight: 700, padding: "1rem 2rem", borderRadius: "0.5rem", border: "none", cursor: "pointer", width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, fontSize: "1rem" },
  fileRow: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "1rem 1.25rem", backgroundColor: "#f1f5f9", borderRadius: "0.5rem" },
  progressBox: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, padding: "1.5rem" },
  waveformMock: { height: 60, display: "flex", alignItems: "center", gap: 2, padding: "0 1rem" },
  bar: (h, active) => ({ flex: 1, backgroundColor: active ? PRIMARY : NEUTRAL, height: `${h}%`, borderRadius: "9999px", transition: "height 0.3s, background-color 0.3s" }),
  verdictBadge: (v) => ({
    padding: "0.375rem 0.875rem",
    backgroundColor: v === "FAKE" ? "#fff1f2" : v === "REAL" ? "#f0fdf4" : "#fef3c7",
    color: v === "FAKE" ? "#e11d48" : v === "REAL" ? "#059669" : "#b45309",
    fontSize: "0.75rem", fontWeight: 800, borderRadius: "9999px", textTransform: "uppercase", letterSpacing: "0.05em"
  }),
  resultGrid: { display: "grid", gridTemplateColumns: "1fr 2fr", gap: "1.5rem" },
  metricRow: { marginBottom: "1.25rem" },
  metricLabel: { display: "flex", justifySpace: "between", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" },
  track: { height: 8, backgroundColor: NEUTRAL, borderRadius: "9999px", overflow: "hidden" },
  fill: (w, color) => ({ height: "100%", width: `${w}%`, backgroundColor: color, borderRadius: "9999px", transition: "width 0.8s ease-out" }),
  errorBox: { backgroundColor: "#fff1f2", border: "1px solid #fecdd3", borderRadius: "0.5rem", padding: "0.75rem 1rem", color: "#e11d48", fontSize: "0.875rem", fontWeight: 600 },
};

export default function AudioScanPage({ onNavigate }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleFile = (f) => {
    if (!f) return;
    if (!f.type.startsWith("audio/")) { setError("Please upload an audio file."); return; }
    setError(""); setFile(f); setResult(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setError(""); setResult(null); setLoading(true); setProgress(0);

    const stages = [
      "Vocal Biometrics Extraction...",
      "Spectral Consistency Check...",
      "Neural Artifact Analysis...",
      "Consensus Verdict Aggregation..."
    ];
    let sIdx = 0;
    setStage(stages[0]);
    const intv = setInterval(() => {
      sIdx++;
      if (sIdx < stages.length) {
        setStage(stages[sIdx]);
        setProgress(Math.round((sIdx / stages.length) * 90));
      }
    }, 1800);

    try {
      const data = await detectAudio(file);
      setProgress(100);
      setResult(data);
    } catch (e) {
      setError(e.message || "Analysis failed.");
    } finally {
      clearInterval(intv);
      setLoading(false);
      setStage("");
    }
  };

  const clear = () => { setFile(null); setResult(null); setError(""); setProgress(0); };

  return (
    <div style={s.root}>
      {/* Header */}
      <header style={s.header}>
        <div style={s.logoRow}>
          <div style={s.logoIcon}>
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>analytics</span>
          </div>
          <h2 style={s.logoText}>AudioScan AI</h2>
        </div>
        <nav style={s.nav}>
          <button style={s.navLink} onClick={() => onNavigate("landing")}>Home</button>
          <button style={s.navLink} onClick={() => onNavigate("video")}>Video Scan</button>
          <button style={s.navLink} onClick={() => onNavigate("image")}>Image Scan</button>
          <button style={s.navLinkActive}>Audio Scan</button>
        </nav>
      </header>

      <main style={s.main}>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", itemsCenter: "center", gap: 8, fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em" }}>
            <span>Forensics</span>
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>chevron_right</span>
            <span style={{ color: PRIMARY }}>Audio Analysis</span>
          </div>
          <h1 style={s.pageTitle}>Deepfake Detection Lab</h1>
          <p style={s.pageSub}>Advanced vocal biometrics and artifact analysis for digital evidence verification.</p>
        </div>

        {!file ? (
          <div style={s.uploadCard} onClick={() => fileRef.current.click()}>
            <div style={s.uploadIcon}>
              <span className="material-symbols-outlined" style={{ fontSize: 32 }}>cloud_upload</span>
            </div>
            <div>
              <h3 style={{ fontSize: "1.125rem", fontWeight: 700, margin: "0 0 6px" }}>Drop audio forensics sample</h3>
              <p style={{ fontSize: "0.875rem", color: "#64748b", margin: 0 }}>Supports High-Fidelity WAV, MP3, or M4A (Max 50MB)</p>
            </div>
            <button style={s.btnPrimary}>Select Evidence File</button>
            <input ref={fileRef} type="file" accept="audio/*" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            <div style={{ ...s.card, padding: "1.5rem" }}>
              <div style={s.fileRow}>
                <div style={{ display: "flex", itemsCenter: "center", gap: 12 }}>
                  <span className="material-symbols-outlined" style={{ color: PRIMARY, fontSize: 24 }}>mic_external_on</span>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: "0.875rem", color: "#1e293b" }}>{file.name}</div>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>{(file.size/1024/1024).toFixed(2)} MB • Forensic Sample</div>
                  </div>
                </div>
                <button style={{ background: "none", border: "none", color: "#94a3b8", cursor: "pointer", fontSize: 20 }} onClick={clear}>✕</button>
              </div>
              {!result && !loading && (
                <button style={{ ...s.btnPrimaryLg, marginTop: "1rem" }} onClick={handleAnalyze}>
                  <span className="material-symbols-outlined">psychology</span>
                  Run Forensic Analysis
                </button>
              )}
            </div>

            {loading && (
              <div style={s.progressBox}>
                <div style={{ display: "flex", justifySpace: "between", marginBottom: "1rem" }}>
                  <div style={{ display: "flex", itemsCenter: "center", gap: 8, fontSize: "0.875rem", fontWeight: 700 }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: PRIMARY, animation: "pulse 1s infinite" }}></div>
                    Analysing vocal patterns...
                  </div>
                  <span style={{ fontSize: "0.875rem", fontWeight: 700, color: PRIMARY }}>{progress}%</span>
                </div>
                <div style={s.waveformMock}>
                  {[40, 60, 30, 80, 95, 70, 40, 60, 85, 50, 30, 65, 45, 75, 25, 90, 40, 60, 30, 80, 55].map((h, i) => (
                    <div key={i} style={s.bar(h, i < (progress / 5))} />
                  ))}
                </div>
                <div style={{ ...s.track, marginTop: "1.5rem" }}>
                  <div style={s.fill(progress, PRIMARY)} />
                </div>
                {stage && <div style={{ fontSize: "0.75rem", color: PRIMARY, fontWeight: 700, marginTop: 8, fontStyle: "italic" }}>{stage}</div>}
              </div>
            )}

            {result && (
              <div style={s.resultGrid}>
                <div style={{ ...s.card, padding: "2rem", display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
                   <p style={{ fontSize: "0.625rem", fontWeight: 800, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "1rem" }}>Verdict</p>
                   <div style={s.verdictBadge(result.verdict)}>{result.verdict}</div>
                   <div style={{ fontSize: "3rem", fontWeight: 900, color: "#0f172a", margin: "1.5rem 0 0" }}>{Math.round(result.confidence || 0)}%</div>
                   <p style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 500 }}>Confidence Score</p>
                </div>

                <div style={{ ...s.card, padding: "1.5rem" }}>
                  <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1.5rem" }}>Vocal Artifact Analysis</h3>
                  <div style={s.metricRow}>
                    <div style={s.metricLabel}>
                      <span>Frequency Consistency</span>
                      <span style={{ color: result?.ai_patterns?.frequency_consistency === "FAIL" ? "#e11d48" : "#059669" }}>
                        {result?.ai_patterns?.frequency_consistency === "FAIL" ? "Anomalous" : "Natural"}
                      </span>
                    </div>
                    <div style={s.track}>
                      <div style={s.fill(result?.ai_patterns?.frequency_consistency === "FAIL" ? 88 : 12, result?.ai_patterns?.frequency_consistency === "FAIL" ? "#e11d48" : "#059669")} />
                    </div>
                    <p style={{ fontSize: "0.75rem", color: "#64748b", marginTop: 6, fontStyle: "italic" }}>Based on High-Frequency spectral ratio and centroid stability.</p>
                  </div>
                  <div style={s.metricRow}>
                    <div style={s.metricLabel}>
                      <span>Phase Discontinuity</span>
                      <span style={{ color: result?.ai_patterns?.phase_discontinuity === "FAIL" ? "#e11d48" : "#059669" }}>
                        {result?.ai_patterns?.phase_discontinuity === "FAIL" ? "High Risk" : "Stable"}
                      </span>
                    </div>
                    <div style={s.track}>
                      <div style={s.fill(result?.ai_patterns?.phase_discontinuity === "FAIL" ? 88 : 12, result?.ai_patterns?.phase_discontinuity === "FAIL" ? "#e11d48" : "#059669")} />
                    </div>
                    <p style={{ fontSize: "0.75rem", color: "#64748b", marginTop: 6, fontStyle: "italic" }}>Based on Spectral Flux energy transitions.</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {error && <div style={s.errorBox}>{error}</div>}
      </main>
      <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }`}</style>
    </div>
  );
}
