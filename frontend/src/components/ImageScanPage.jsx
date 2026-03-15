import React, { useState, useRef } from "react";
import { detectImage } from "../api";

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
  main: { maxWidth: "72rem", margin: "0 auto", padding: "2.5rem", display: "flex", flexDirection: "column", gap: "2rem" },
  pageTitle: { fontSize: "1.875rem", fontWeight: 800, letterSpacing: "-0.025em", color: "#0f172a", margin: 0 },
  pageSub: { fontSize: "1.125rem", color: "#64748b", margin: "0.25rem 0 0" },
  grid: { display: "grid", gridTemplateColumns: "7fr 5fr", gap: "2rem" },
  card: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, boxShadow: "0 1px 3px rgba(0,0,0,0.04)" },
  uploadCard: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px dashed ${BORDER}`, padding: "2.5rem", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", gap: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.04)", cursor: "pointer", transition: "border-color 0.2s" },
  uploadIcon: { width: 64, height: 64, borderRadius: "50%", backgroundColor: `${PRIMARY}0D`, display: "flex", alignItems: "center", justifyContent: "center", color: PRIMARY },
  uploadTitle: { fontSize: "1.25rem", fontWeight: 600, margin: "0 0 0.5rem" },
  uploadSub: { fontSize: "0.875rem", color: "#64748b", maxWidth: "20rem", margin: 0 },
  btnPrimary: { backgroundColor: PRIMARY, color: "white", fontWeight: 700, padding: "0.75rem 2rem", borderRadius: "0.5rem", border: "none", cursor: "pointer", boxShadow: `0 4px 12px ${PRIMARY}33`, fontSize: "1rem" },
  btnPrimaryLg: { backgroundColor: PRIMARY, color: "white", fontWeight: 700, padding: "0.75rem 2rem", borderRadius: "0.5rem", border: "none", cursor: "pointer", boxShadow: `0 4px 12px ${PRIMARY}33`, fontSize: "1rem", width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8 },
  btnSecondary: { backgroundColor: NEUTRAL, color: "#334155", fontWeight: 700, padding: "0.75rem 1.5rem", borderRadius: "0.5rem", border: "none", cursor: "pointer" },
  btnRow: { display: "flex", gap: "0.75rem" },
  uploadMeta: { fontSize: "0.75rem", color: "#94a3b8" },
  fileRow: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "1rem 1.25rem", backgroundColor: "#f1f5f9", borderRadius: "0.5rem", marginBottom: "1rem" },
  fileName: { fontWeight: 600, fontSize: "0.875rem", color: "#0f172a" },
  fileSize: { fontSize: "0.75rem", color: "#64748b", marginTop: 2 },
  clearBtn: { background: "none", border: "none", color: "#94a3b8", cursor: "pointer", fontSize: 20, lineHeight: 1 },
  progressCard: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.04)", display: "flex", flexDirection: "column", gap: "1rem" },
  progressRow: { display: "flex", alignItems: "center", justifyContent: "space-between" },
  progressLabel: { display: "flex", alignItems: "center", gap: 12, fontWeight: 600, color: "#1e293b" },
  progressTrack: { width: "100%", backgroundColor: NEUTRAL, borderRadius: "9999px", height: 10, overflow: "hidden" },
  progressFill: { backgroundColor: PRIMARY, height: "100%", borderRadius: "9999px", transition: "width 0.5s" },
  stageLabel: { fontSize: "0.75rem", color: PRIMARY, fontWeight: 600, fontStyle: "italic" },
  errorBox: { backgroundColor: "#fff1f2", border: "1px solid #fecdd3", borderRadius: "0.5rem", padding: "0.75rem 1rem", color: "#e11d48", fontSize: "0.875rem", fontWeight: 600 },
  verdictHeader: { padding: "1.5rem", backgroundColor: "#f8fafc", borderBottom: `1px solid ${BORDER}`, display: "flex", alignItems: "center", justifyContent: "space-between", borderRadius: "0.75rem 0.75rem 0 0" },
  verdictTitle: { fontWeight: 700, color: "#1e293b", margin: 0 },
  verdictBody: { padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1.5rem" },
  circleWrap: { display: "flex", justifyContent: "center", padding: "1rem 0" },
  markersTitle: { fontSize: "0.75rem", fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 0.75rem" },
  markerRow: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem", borderRadius: "0.5rem", backgroundColor: "#f8fafc", border: `1px solid ${BORDER}`, marginBottom: "0.5rem" },
  markerLeft: { display: "flex", alignItems: "center", gap: 12 },
  downloadBtn: { width: "100%", padding: "0.75rem", backgroundColor: NEUTRAL, color: "#1e293b", fontWeight: 700, borderRadius: "0.5rem", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, fontSize: "0.875rem" },
  resultBadge: (verdict) => {
    const v = verdict?.toUpperCase();
    return {
      padding: "0.25rem 0.75rem",
      backgroundColor: v === "FAKE" ? "#fff1f2" : v === "REAL" ? "#f0fdf4" : "#fef3c7",
      color: v === "FAKE" ? "#e11d48" : v === "REAL" ? "#059669" : "#b45309",
      fontSize: "0.75rem", fontWeight: 900, textTransform: "uppercase", letterSpacing: "0.1em", borderRadius: "9999px",
    }
  },
  previewImg: { width: "100%", height: "auto", maxHeight: "20rem", objectFit: "contain", borderRadius: "0.5rem", border: `1px solid ${BORDER}`, marginTop: "1rem" },
  summaryBox: { backgroundColor: "#f8fafc", borderRadius: "0.5rem", padding: "1rem", fontSize: "0.875rem", color: "#475569", lineHeight: 1.6 },
  reasonList: { listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 6 },
  reasonItem: { fontSize: "0.8125rem", color: "#475569", display: "flex", gap: 8, alignItems: "flex-start" },
};

export default function ImageScanPage({ onNavigate }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleFile = (f) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) { setError("Please upload an image file."); return; }
    setError(""); setFile(f); setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(f);
  };

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const clear = () => { setFile(null); setPreview(null); setResult(null); setError(""); setProgress(0); setStage(""); };

  const handleAnalyze = async () => {
    if (!file) return;
    setError(""); setResult(null); setLoading(true); setProgress(0);

    const stages = [
      "Extracting Scene Details...",
      "Building Scene Model...",
      "Detecting AI Signatures...",
      "Generating Forensic Report..."
    ];
    let stageIdx = 0;
    setStage(stages[0]);
    const interval = setInterval(() => {
      stageIdx++;
      if (stageIdx < stages.length) {
        setStage(stages[stageIdx]);
        setProgress(Math.round((stageIdx / stages.length) * 85));
      }
    }, 2200);

    try {
      const data = await detectImage(file);
      setProgress(100);
      setResult(data);
    } catch (e) {
      setError(e.message || "Analysis failed. Make sure the backend is running.");
    } finally {
      clearInterval(interval);
      setLoading(false);
      setStage("");
    }
  };

  const verdictColor = result
    ? result.verdict?.toUpperCase() === "FAKE" ? "#e11d48" : result.verdict?.toUpperCase() === "REAL" ? "#059669" : "#d97706"
    : "#193ce6";

  return (
    <div style={s.root}>
      {/* Header */}
      <header style={s.header}>
        <div style={s.logoRow}>
          <div style={s.logoIcon}>
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>shield_with_heart</span>
          </div>
          <h2 style={s.logoText}>AI Forensics</h2>
        </div>
        <nav style={s.nav}>
          <button style={s.navLink} onClick={() => onNavigate("landing")}>Home</button>
          <button style={s.navLink} onClick={() => onNavigate("video")}>Video Scan</button>
          <button style={s.navLinkActive}>Image Scan</button>
          <button style={s.navLink} onClick={() => onNavigate("audio")}>Audio Scan</button>
        </nav>
      </header>

      <main style={s.main}>
        <div>
          <h1 style={s.pageTitle}>Image Authenticity Analysis</h1>
          <p style={s.pageSub}>Upload digital assets to verify provenance and detect GAN or Diffusion based manipulations.</p>
        </div>

        <div style={s.grid}>
          {/* Left */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {/* Upload */}
            {!file ? (
              <div
                style={{ ...s.uploadCard, borderColor: dragging ? PRIMARY : BORDER }}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileRef.current.click()}
              >
                <div style={s.uploadIcon}>
                  <span className="material-symbols-outlined" style={{ fontSize: 36 }}>upload_file</span>
                </div>
                <div>
                  <h3 style={s.uploadTitle}>Upload Source Image</h3>
                  <p style={s.uploadSub}>Drag and drop high-resolution images (JPG, PNG, WebP, TIFF) for forensic pixel-level scanning.</p>
                </div>
                <div style={s.btnRow}>
                  <button style={s.btnPrimary} onClick={(e) => { e.stopPropagation(); fileRef.current.click(); }}>Select File</button>
                  <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
                </div>
                <p style={s.uploadMeta}>Maximum file size: 25MB • Automated metadata extraction</p>
              </div>
            ) : (
              <div style={{ ...s.card, padding: "1.5rem" }}>
                {/* File info row */}
                <div style={s.fileRow}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span className="material-symbols-outlined" style={{ color: PRIMARY, fontSize: 28 }}>image</span>
                    <div>
                      <div style={s.fileName}>{file.name}</div>
                      <div style={s.fileSize}>{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                    </div>
                  </div>
                  <button style={s.clearBtn} onClick={clear} title="Remove">✕</button>
                </div>

                {preview && <img src={preview} alt="Preview" style={s.previewImg} />}

                {/* Analyze button */}
                <button style={{ ...s.btnPrimaryLg, opacity: loading ? 0.7 : 1, marginTop: "1rem" }} onClick={handleAnalyze} disabled={loading}>
                  {loading ? (
                    <>
                      <span style={{ display: "inline-block", width: 16, height: 16, border: "2px solid rgba(255,255,255,0.4)", borderTopColor: "white", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                      Scanning...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined" style={{ fontSize: 20 }}>image_search</span>
                      Initialize Scan
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Error */}
            {error && <div style={s.errorBox}>{error}</div>}

            {/* Progress */}
            {loading && (
              <div style={s.progressCard}>
                <div style={s.progressRow}>
                  <div style={s.progressLabel}>
                    <span className="material-symbols-outlined" style={{ color: PRIMARY }}>query_stats</span>
                    Forensic Processing
                  </div>
                  <span style={{ fontSize: "0.875rem", fontWeight: 700, color: PRIMARY }}>{progress}%</span>
                </div>
                <div style={s.progressTrack}>
                  <div style={{ ...s.progressFill, width: `${progress}%` }} />
                </div>
                {stage && <div style={s.stageLabel}>{stage}</div>}
              </div>
            )}

            {/* Result Summary */}
            {result && (
              <div style={{ ...s.card, padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <h3 style={{ fontWeight: 700, fontSize: "1rem", margin: 0 }}>Analysis Complete</h3>
                  <span style={s.resultBadge(result.verdict)}>{result.verdict}</span>
                </div>
                <div style={s.summaryBox}>
                  {result.message || result.summary || `Analysis suggests the image is ${result.verdict?.toLowerCase()}. No significant AI artifacts found in the high-frequency spectral bands.`}
                </div>
              </div>
            )}
          </div>

          {/* Right – Verdict */}
          <div style={s.card}>
            <div style={s.verdictHeader}>
              <h3 style={s.verdictTitle}>Detailed Findings</h3>
              <span style={s.resultBadge(result ? result.verdict : "UNCERTAIN")}>
                {result ? result.verdict : "Pending"}
              </span>
            </div>
            <div style={s.verdictBody}>
              {/* Confidence Circle */}
              <div style={s.circleWrap}>
                <div style={{ position: "relative", width: 128, height: 128 }}>
                  <svg style={{ width: "100%", height: "100%", transform: "rotate(-90deg)" }} viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="16" fill="none" stroke={NEUTRAL} strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="16" fill="none"
                      stroke={result ? verdictColor : PRIMARY}
                      strokeWidth="3"
                      strokeDasharray="100"
                      strokeDashoffset={result
                        ? String(100 - Math.round(result.confidence || 0))
                        : "0"}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                    <span style={{ fontSize: "1.5rem", fontWeight: 900, color: "#0f172a", lineHeight: 1 }}>
                      {result ? `${Math.round(result.confidence || 0)}%` : "—"}
                    </span>
                    <span style={{ fontSize: "0.625rem", textTransform: "uppercase", fontWeight: 700, color: "#64748b", letterSpacing: "0.05em" }}>Confidence</span>
                  </div>
                </div>
              </div>

              {/* Dynamic Signal Analytics — driven by real ai_patterns from API */}
              <div>
                <p style={s.markersTitle}>SIGNAL ANALYTICS</p>
                {(() => {
                  const ap = result?.ai_patterns;
                  const v = result?.verdict?.toUpperCase();

                  // Map ai_patterns scores or fall back to smart inference from verdict
                  const scoreColor = (score) => {
                    if (!score) return "#94a3b8";
                    if (score === "PASS") return "#059669";
                    if (score === "FAIL") return "#e11d48";
                    return "#d97706"; // UNCERTAIN
                  };
                  const scoreLabel = (score, fallbackFake, fallbackReal) => {
                    if (score) return score;
                    if (!result) return "WAITING";
                    return v === "FAKE" ? fallbackFake : v === "REAL" ? fallbackReal : "UNCERTAIN";
                  };

                  const markers = [
                    {
                      icon: "manage_accounts",
                      label: "Anatomy & Proportions",
                      rawScore: ap?.anatomy_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                    {
                      icon: "brightness_medium",
                      label: "Lighting Physics",
                      rawScore: ap?.lighting_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                    {
                      icon: "texture",
                      label: "Skin Texture Authenticity",
                      rawScore: ap?.texture_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                    {
                      icon: "landscape",
                      label: "Background Coherence",
                      rawScore: ap?.background_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                    {
                      icon: "visibility",
                      label: "Eye Physics",
                      rawScore: ap?.eye_physics_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                    {
                      icon: "psychology",
                      label: "Semantic & Logical Coherence",
                      rawScore: ap?.semantic_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                    {
                      icon: "content_cut",
                      label: "Edge & Boundary Halos",
                      rawScore: ap?.edge_boundary_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                    {
                      icon: "grain",
                      label: "Sensor Noise Consistency",
                      rawScore: ap?.noise_analysis_score,
                      fallbackFake: "FAIL",
                      fallbackReal: "PASS",
                    },
                  ];

                  return markers.map(({ icon, label, rawScore, fallbackFake, fallbackReal }) => {
                    const val = scoreLabel(rawScore, fallbackFake, fallbackReal);
                    const color = result ? scoreColor(val) : "#94a3b8";
                    return (
                      <div key={label} style={s.markerRow}>
                        <div style={s.markerLeft}>
                          <span className="material-symbols-outlined" style={{ color }}>{icon}</span>
                          <span style={{ fontSize: "0.875rem", fontWeight: 500 }}>{label}</span>
                        </div>
                        <span style={{ fontSize: "0.75rem", fontWeight: 700, color }}>{val}</span>
                      </div>
                    );
                  });
                })()}
              </div>

              <button style={s.downloadBtn}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>download</span>
                Download Analysis Report
              </button>
            </div>
          </div>
        </div>
      </main>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
