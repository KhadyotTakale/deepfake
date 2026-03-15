import React, { useState, useRef } from "react";

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
  navLinkActive: { fontSize: "0.875rem", fontWeight: 700, color: PRIMARY, background: "none", borderBottom: `2px solid ${PRIMARY}`, border: "none", cursor: "pointer", padding: "0.25rem 0", paddingBottom: "0.5rem" },
  main: { maxWidth: "72rem", margin: "0 auto", padding: "2.5rem", display: "flex", flexDirection: "column", gap: "2rem" },
  pageTitle: { fontSize: "1.875rem", fontWeight: 800, letterSpacing: "-0.025em", color: "#0f172a", margin: 0 },
  pageSub: { fontSize: "1.125rem", color: "#64748b", margin: "0.25rem 0 0" },
  grid: { display: "grid", gridTemplateColumns: "7fr 5fr", gap: "2rem" },
  card: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, boxShadow: "0 1px 3px rgba(0,0,0,0.04)" },
  uploadCard: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, padding: "2.5rem", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", gap: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.04)" },
  uploadIcon: { width: 64, height: 64, borderRadius: "50%", backgroundColor: `${PRIMARY}0D`, display: "flex", alignItems: "center", justifyContent: "center", color: PRIMARY },
  uploadTitle: { fontSize: "1.25rem", fontWeight: 600, margin: "0 0 0.5rem" },
  uploadSub: { fontSize: "0.875rem", color: "#64748b", maxWidth: "20rem", margin: 0 },
  btnPrimary: { backgroundColor: PRIMARY, color: "white", fontWeight: 700, padding: "0.625rem 1.5rem", borderRadius: "0.5rem", border: "none", cursor: "pointer", boxShadow: `0 4px 12px ${PRIMARY}33` },
  btnSecondary: { backgroundColor: NEUTRAL, color: "#334155", fontWeight: 700, padding: "0.625rem 1.5rem", borderRadius: "0.5rem", border: "none", cursor: "pointer" },
  btnRow: { display: "flex", gap: "0.75rem" },
  uploadMeta: { fontSize: "0.75rem", color: "#94a3b8" },
  progressCard: { backgroundColor: "white", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.04)", display: "flex", flexDirection: "column", gap: "1rem" },
  progressRow: { display: "flex", alignItems: "center", justifyContent: "space-between" },
  progressLabel: { display: "flex", alignItems: "center", gap: 12, fontWeight: 600, color: "#1e293b" },
  progressPct: { fontSize: "0.875rem", fontWeight: 700, color: PRIMARY },
  progressTrack: { width: "100%", backgroundColor: NEUTRAL, borderRadius: "9999px", height: 10, overflow: "hidden" },
  progressFill: { backgroundColor: PRIMARY, height: "100%", borderRadius: "9999px", transition: "width 0.5s" },
  progressMeta: { display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#64748b" },
  verdictHeader: { padding: "1.5rem", backgroundColor: "#f8fafc", borderBottom: `1px solid ${BORDER}`, display: "flex", alignItems: "center", justifyContent: "space-between", borderRadius: "0.75rem 0.75rem 0 0" },
  verdictTitle: { fontWeight: 700, color: "#1e293b", margin: 0 },
  verdictBadge: { padding: "0.25rem 0.75rem", backgroundColor: "#fef3c7", color: "#b45309", fontSize: "0.75rem", fontWeight: 900, textTransform: "uppercase", letterSpacing: "0.1em", borderRadius: "9999px" },
  verdictBody: { padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1.5rem" },
  circleWrap: { display: "flex", justifyContent: "center", padding: "1rem 0" },
  markersTitle: { fontSize: "0.75rem", fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 0.75rem" },
  markerRow: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem", borderRadius: "0.5rem", backgroundColor: "#f8fafc", border: `1px solid ${BORDER}`, marginBottom: "0.5rem" },
  markerLeft: { display: "flex", alignItems: "center", gap: 12 },
  markerLabel: { fontSize: "0.875rem", fontWeight: 500 },
  downloadBtn: { width: "100%", padding: "0.75rem", backgroundColor: NEUTRAL, color: "#1e293b", fontWeight: 700, borderRadius: "0.5rem", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, fontSize: "0.875rem" },
  recentTitle: { fontSize: "1.25rem", fontWeight: 700, color: "#0f172a", margin: 0 },
  recentHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" },
  recentGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" },
  recentCard: { backgroundColor: "white", padding: "1rem", borderRadius: "0.75rem", border: `1px solid ${BORDER}`, display: "flex", alignItems: "center", gap: "1rem", cursor: "pointer", boxShadow: "0 1px 3px rgba(0,0,0,0.04)" },
  recentThumb: { width: 48, height: 48, borderRadius: "0.5rem", backgroundColor: "#e2e8f0", overflow: "hidden", position: "relative", flexShrink: 0 },
  recentInfo: { flexGrow: 1, overflow: "hidden" },
  recentName: { fontWeight: 700, fontSize: "0.875rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", margin: 0 },
  recentMeta: { display: "flex", alignItems: "center", gap: 8, marginTop: 4 },
};

export default function VideoScanPage({ onNavigate }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef();

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  };

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
          <button style={s.navLinkActive}>Video Scan</button>
          <button style={s.navLink} onClick={() => onNavigate("image")}>Image Scan</button>
          <button style={s.navLink} onClick={() => onNavigate("audio")}>Audio Scan</button>
        </nav>
      </header>

      <main style={s.main}>
        {/* Page Title */}
        <div>
          <h1 style={s.pageTitle}>Video Integrity Analysis</h1>
          <p style={s.pageSub}>Deploy neural engine forensics to detect synthetic manipulations and deepfakes.</p>
        </div>

        {/* Two-col grid */}
        <div style={s.grid}>
          {/* Left */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {/* Upload */}
            <div
              style={{ ...s.uploadCard, border: dragging ? `2px dashed ${PRIMARY}` : `1px solid ${BORDER}` }}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >
              <div style={s.uploadIcon}>
                <span className="material-symbols-outlined" style={{ fontSize: 36 }}>upload_file</span>
              </div>
              <div>
                <h3 style={s.uploadTitle}>{file ? file.name : "Upload Source Media"}</h3>
                <p style={s.uploadSub}>Drag and drop high-resolution video files (MP4, MOV, AVI) for frame-by-frame forensic scanning.</p>
              </div>
              <div style={s.btnRow}>
                <button style={s.btnPrimary} onClick={() => fileRef.current.click()}>Select File</button>
                <button style={s.btnSecondary}>Paste URL</button>
                <input ref={fileRef} type="file" accept="video/*" style={{ display: "none" }} onChange={e => setFile(e.target.files[0])} />
              </div>
              <p style={s.uploadMeta}>Maximum file size: 500MB • End-to-end encrypted processing</p>
            </div>

            {/* Progress */}
            <div style={s.progressCard}>
              <div style={s.progressRow}>
                <div style={s.progressLabel}>
                  <span className="material-symbols-outlined" style={{ color: PRIMARY }}>analytics</span>
                  Processing Analysis
                </div>
                <span style={s.progressPct}>74%</span>
              </div>
              <div style={s.progressTrack}>
                <div style={{ ...s.progressFill, width: "74%" }} />
              </div>
              <div style={s.progressMeta}>
                <span>Artifact scanning: Frame 14,203 of 19,200</span>
                <span style={{ fontStyle: "italic" }}>Estimated time remaining: 12s</span>
              </div>
            </div>
          </div>

          {/* Right – Verdict */}
          <div style={s.card}>
            <div style={s.verdictHeader}>
              <h3 style={s.verdictTitle}>Forensic Verdict</h3>
              <span style={s.verdictBadge}>Uncertain</span>
            </div>
            <div style={s.verdictBody}>
              {/* Circle */}
              <div style={s.circleWrap}>
                <div style={{ position: "relative", width: 128, height: 128 }}>
                  <svg style={{ width: "100%", height: "100%", transform: "rotate(-90deg)" }} viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="16" fill="none" stroke={NEUTRAL} strokeWidth="3" />
                    <circle cx="18" cy="18" r="16" fill="none" stroke={PRIMARY} strokeWidth="3" strokeDasharray="100" strokeDashoffset="35" strokeLinecap="round" />
                  </svg>
                  <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                    <span style={{ fontSize: "1.5rem", fontWeight: 900, color: "#0f172a", lineHeight: 1 }}>65%</span>
                    <span style={{ fontSize: "0.625rem", textTransform: "uppercase", fontWeight: 700, color: "#64748b", letterSpacing: "0.05em" }}>Confidence</span>
                  </div>
                </div>
              </div>

              {/* Markers */}
              <div>
                <p style={s.markersTitle}>Analysis Markers</p>
                {[
                  { icon: "face", label: "Facial Consistency", val: "Low", color: "#e11d48" },
                  { icon: "waves", label: "Audio-Visual Sync", val: "High", color: "#059669" },
                  { icon: "lens_blur", label: "Artifact Detection", val: "Medium", color: "#d97706" },
                ].map(({ icon, label, val, color }) => (
                  <div key={label} style={s.markerRow}>
                    <div style={s.markerLeft}>
                      <span className="material-symbols-outlined" style={{ color }}>{icon}</span>
                      <span style={s.markerLabel}>{label}</span>
                    </div>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, color }}>{val}</span>
                  </div>
                ))}
              </div>

              {/* Reasoning */}
              <div>
                <p style={s.markersTitle}>Forensic Reasoning</p>
                <p style={{ fontSize: "0.875rem", color: "#475569", lineHeight: 1.6, margin: 0 }}>
                  The model detected anomalies in temporal consistency across frames 450-620. Sub-pixel misalignment suggests potential GAN-based synthesis around the jawline, although audio spectral analysis remains consistent with original recording environments.
                </p>
              </div>

              <button style={s.downloadBtn}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>download</span>
                Download Full Forensic Report
              </button>
            </div>
          </div>
        </div>

        {/* Recent Analyses */}
        <div>
          <div style={s.recentHeader}>
            <h3 style={s.recentTitle}>Recent Analyses</h3>
            <button style={{ fontSize: "0.875rem", fontWeight: 700, color: PRIMARY, background: "none", border: "none", cursor: "pointer" }}>View All History</button>
          </div>
          <div style={s.recentGrid}>
            {[
              { name: "interview_final.mp4", verdict: "Fake", verdictColor: "#e11d48", time: "2h ago", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuA8J--uZjRuiMqfrLobKLqt6VKHn8ksxPUlCxC9V9y54H1Q8ugX_6xrYovEeRM0JJXJwRgBxm5Y0tBqBuSfq8WvbWk1FgeNLBh5E83p2vz9FAOUlaSNZMiTNTXYfwf0mxG_noj8rfRB8co1OCEXbn3vfmORYAdbjWnCKk9KNWeg-yffDI1HXfUmgbDiVRe2Gq7JOdcjD4zTERqnoaZVJROTb3dQCOqpFQDFxagKY1IU0phiKBWGjpzHiUPmTkxwB0xMGgvx328J1wU" },
              { name: "nature_doc_01.mov", verdict: "Real", verdictColor: "#059669", time: "5h ago", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuCGyEk3fQSWhiekEBkUXhZ-6C5hU6YECUtlSiZbGfbD8AZxi142IhgXMV2GlLrGSwA3jJu-VGADfPPAMCcfP24l5KnMOAUTqIsePNPLlzweTHm8eZMDgxDrzSKXvhaBuBfQxAbGLOeXOI9Qh9GgbRhAUKziblIxbn6mZT0ZVsEAxTp-b-51Va-Wuju3gnShthly5VuTOHh71W01MhhBWxscbvH6RtXfz6WKa8Rdjbhm93mvp273g419nd1pkbTnteeihb4EeoBEIZw" },
              { name: "cctv_log_224.avi", verdict: "Real", verdictColor: "#059669", time: "1d ago", img: "https://lh3.googleusercontent.com/aida-public/AB6AXuAFUk1ZJZOTn7xQArXDCkGKXYMZSYlcVckvN-k86eVIWa0LyRH1snw1WiJfSjI4wL6c8pagTaDKREK50wX4bPBS_F-fWcfIEHBME7a-Ryy4AWIUeiXGIS816Ar6dztE2405gKil8VWy4x_vlBjKaiFqvFU21XZRrNhJihdpJ0WZohtvlojW_q9VevryWCc-O1KvFExM0qi7JFhnbKZdhdlWnB4V7ldZGaMF01dmxblytiAxdLwtXtOsckrSygeHAvOB5Q4OgcNcYt8" },
            ].map(({ name, verdict, verdictColor, time, img }) => (
              <div key={name} style={s.recentCard}>
                <div style={s.recentThumb}>
                  <img src={img} alt={name} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  <div style={{ position: "absolute", inset: 0, backgroundColor: "rgba(0,0,0,0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <span className="material-symbols-outlined" style={{ color: "white", fontSize: 18 }}>play_circle</span>
                  </div>
                </div>
                <div style={s.recentInfo}>
                  <p style={s.recentName}>{name}</p>
                  <div style={s.recentMeta}>
                    <span style={{ fontSize: "0.625rem", fontWeight: 900, color: verdictColor, textTransform: "uppercase" }}>{verdict}</span>
                    <span style={{ fontSize: "0.625rem", color: "#94a3b8" }}>• {time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
