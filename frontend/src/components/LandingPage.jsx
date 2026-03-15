import React from "react";

const PRIMARY = "#193ce6";
const ACCENT = "#06b6d4";
const BG = "#f6f6f8";

const styles = {
  root: { backgroundColor: BG, color: "#0f172a", fontFamily: "'Inter', sans-serif", minHeight: "100vh", WebkitFontSmoothing: "antialiased" },
  header: { position: "sticky", top: 0, zIndex: 50, width: "100%", borderBottom: "1px solid #e2e8f0", backgroundColor: "rgba(255,255,255,0.8)", backdropFilter: "blur(12px)", WebkitBackdropFilter: "blur(12px)" },
  headerInner: { maxWidth: "80rem", margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "1rem 1.5rem" },
  logoIcon: { width: 32, height: 32, borderRadius: 8, backgroundColor: PRIMARY, display: "flex", alignItems: "center", justifyContent: "center", color: "white" },
  logoText: { fontSize: "1.25rem", fontWeight: 800, letterSpacing: "-0.025em", color: "#0f172a", margin: 0 },
  logoSpan: { color: PRIMARY },
  nav: { display: "flex", alignItems: "center", gap: "2.5rem" },
  navLink: { fontSize: "0.875rem", fontWeight: 600, color: "#475569", textDecoration: "none", transition: "color 0.2s" },
  loginBtn: { fontSize: "0.875rem", fontWeight: 700, color: "#334155", background: "none", border: "none", cursor: "pointer", padding: "0.5rem 1rem" },
  ctaBtn: { borderRadius: "9999px", backgroundColor: PRIMARY, padding: "0.625rem 1.5rem", fontSize: "0.875rem", fontWeight: 700, color: "white", border: "none", cursor: "pointer", boxShadow: `0 8px 16px ${PRIMARY}33` },
  hero: { padding: "7rem 1.5rem 6rem", maxWidth: "80rem", margin: "0 auto" },
  heroGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "3rem", alignItems: "center" },
  badge: { display: "inline-flex", alignItems: "center", gap: 8, borderRadius: "9999px", border: `1px solid ${PRIMARY}33`, backgroundColor: `${PRIMARY}0D`, padding: "0.25rem 0.75rem", fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: PRIMARY, marginBottom: "1rem" },
  dot: { width: 8, height: 8, borderRadius: "50%", backgroundColor: PRIMARY, position: "relative" },
  h1: { fontSize: "4.5rem", fontWeight: 900, lineHeight: 1.1, letterSpacing: "-0.025em", color: "#0f172a", margin: "0 0 1.5rem" },
  gradientText: { background: `linear-gradient(90deg, ${PRIMARY}, ${ACCENT})`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" },
  heroParagraph: { fontSize: "1.125rem", lineHeight: 1.7, color: "#475569", maxWidth: "36rem", margin: "0 0 2rem" },
  btnRow: { display: "flex", alignItems: "center", flexWrap: "wrap", gap: "1rem", marginBottom: "2rem" },
  analyzeBtnHero: { display: "flex", alignItems: "center", gap: 8, borderRadius: "0.75rem", backgroundColor: PRIMARY, padding: "1rem 2rem", fontSize: "1rem", fontWeight: 700, color: "white", border: "none", cursor: "pointer", boxShadow: `0 12px 24px ${PRIMARY}40` },
  demoBtn: { display: "flex", alignItems: "center", gap: 8, borderRadius: "0.75rem", border: "1px solid #e2e8f0", backgroundColor: "white", padding: "1rem 2rem", fontSize: "1rem", fontWeight: 700, color: "#0f172a", cursor: "pointer" },
  trustRow: { display: "flex", alignItems: "center", gap: "1.5rem", flexWrap: "wrap", fontSize: "0.875rem", fontWeight: 500, color: "#94a3b8" },
  trustItem: { display: "flex", alignItems: "center", gap: 4 },
  checkIcon: { color: "#22c55e", fontSize: 18 },
  imageCard: { position: "relative", zIndex: 10, borderRadius: "1rem", border: "1px solid #e2e8f0", backgroundColor: "white", padding: 8, boxShadow: "0 4px 20px -2px rgba(25,60,230,0.05)" },
  imageInner: { borderRadius: "0.75rem", overflow: "hidden", position: "relative", aspectRatio: "16/9" },
  scanImg: { width: "100%", height: "100%", objectFit: "cover" },
  scanOverlay: { position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(15,23,42,0.5), transparent)", display: "flex", alignItems: "flex-end", padding: "1rem" },
  scanBar: { width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", borderRadius: 8, backgroundColor: "rgba(255,255,255,0.1)", padding: "0.75rem 1rem", backdropFilter: "blur(8px)", border: "1px solid rgba(255,255,255,0.2)" },
  scanLabel: { fontSize: "0.625rem", fontWeight: 700, textTransform: "uppercase", opacity: 0.7, color: "white" },
  scanName: { fontSize: "0.875rem", fontWeight: 600, color: "white" },
  confidence: { textAlign: "right" },
  confidenceVal: { fontSize: "0.875rem", fontWeight: 700, color: ACCENT, letterSpacing: "0.1em" },
  trust: { borderTop: "1px solid #f1f5f9", borderBottom: "1px solid #f1f5f9", backgroundColor: "white", padding: "3rem 1.5rem" },
  trustInner: { maxWidth: "80rem", margin: "0 auto", textAlign: "center" },
  trustTitle: { fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "#94a3b8", marginBottom: "2rem" },
  logoRow: { display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "center", gap: "3rem", filter: "grayscale(1)", opacity: 0.4 },
  logoName: { fontSize: "1.5rem", fontWeight: 900 },
  capabilities: { backgroundColor: "#f8fafc", padding: "6rem 1.5rem" },
  capabilitiesInner: { maxWidth: "80rem", margin: "0 auto" },
  capHeader: { textAlign: "center", marginBottom: "4rem" },
  capLabel: { fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: PRIMARY, marginBottom: "1rem" },
  capH2: { fontSize: "2.75rem", fontWeight: 900, letterSpacing: "-0.025em", color: "#0f172a", maxWidth: "40rem", margin: "0 auto 1.5rem" },
  capSub: { fontSize: "1.125rem", color: "#475569", maxWidth: "36rem", margin: "0 auto" },
  cardsGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.5rem" },
  card: { display: "flex", flexDirection: "column", gap: "1.5rem", borderRadius: "1rem", border: "1px solid #e2e8f0", backgroundColor: "white", padding: "2rem", transition: "all 0.3s" },
  cardIcon: { width: 56, height: 56, borderRadius: "0.75rem", backgroundColor: "#f8fafc", display: "flex", alignItems: "center", justifyContent: "center", color: PRIMARY, fontSize: 28 },
  cardTitle: { fontSize: "1.25rem", fontWeight: 700, color: "#0f172a", marginBottom: "0.75rem" },
  cardText: { color: "#475569", lineHeight: 1.6 },
  cardList: { listStyle: "none", padding: 0, margin: "0.5rem 0 0", display: "flex", flexDirection: "column", gap: 8, fontSize: "0.875rem", fontWeight: 500, color: "#64748b" },
  cardListItem: { display: "flex", alignItems: "center", gap: 6 },
  taskIcon: { color: PRIMARY, fontSize: 16 },
  stats: { backgroundColor: "white", padding: "6rem 1.5rem" },
  statsInner: { maxWidth: "80rem", margin: "0 auto" },
  statsGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "2rem" },
  statCard: { borderRadius: "1rem", border: "1px solid #f1f5f9", backgroundColor: "#f8fafc80", padding: "2rem", textAlign: "center" },
  statNum: { fontSize: "2.25rem", fontWeight: 900, color: PRIMARY, marginBottom: "0.5rem" },
  statLabel: { fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "#64748b" },
  cta: { padding: "6rem 1.5rem" },
  ctaInner: { maxWidth: "80rem", margin: "0 auto", borderRadius: "2rem", backgroundColor: "#0f172a", padding: "5rem", position: "relative", overflow: "hidden", textAlign: "center" },
  ctaDots: { position: "absolute", inset: 0, opacity: 0.1, backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)", backgroundSize: "40px 40px" },
  ctaContent: { position: "relative", zIndex: 10 },
  ctaH2: { fontSize: "3.5rem", fontWeight: 900, color: "white", lineHeight: 1.2, maxWidth: "40rem", margin: "0 auto 2rem" },
  ctaP: { fontSize: "1.125rem", color: "#94a3b8", maxWidth: "36rem", margin: "0 auto 3rem" },
  ctaBtnRow: { display: "flex", justifyContent: "center", gap: "1rem", flexWrap: "wrap" },
  ctaStartBtn: { borderRadius: "0.75rem", backgroundColor: PRIMARY, padding: "1.25rem 2.5rem", fontSize: "1.125rem", fontWeight: 700, color: "white", border: "none", cursor: "pointer" },
  ctaExpertBtn: { borderRadius: "0.75rem", border: "1px solid rgba(255,255,255,0.2)", backgroundColor: "rgba(255,255,255,0.05)", padding: "1.25rem 2.5rem", fontSize: "1.125rem", fontWeight: 700, color: "white", cursor: "pointer", backdropFilter: "blur(8px)" },
  footer: { backgroundColor: "#f8fafc", borderTop: "1px solid #e2e8f0", padding: "5rem 1.5rem 2.5rem" },
  footerInner: { maxWidth: "80rem", margin: "0 auto" },
  footerGrid: { display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: "3rem", marginBottom: "5rem" },
  footerBrand: { display: "flex", flexDirection: "column", gap: "1.5rem" },
  footerLogoRow: { display: "flex", alignItems: "center", gap: 8 },
  footerTagline: { fontSize: "0.875rem", lineHeight: 1.7, color: "#64748b" },
  footerHeading: { fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.15em", color: "#0f172a", marginBottom: "1.5rem" },
  footerList: { listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "1rem" },
  footerLink: { fontSize: "0.875rem", fontWeight: 500, color: "#64748b", textDecoration: "none" },
  footerBottom: { borderTop: "1px solid #e2e8f0", paddingTop: "2rem", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" },
  footerCopy: { fontSize: "0.75rem", fontWeight: 500, color: "#94a3b8" },
  footerLinkRow: { display: "flex", gap: "1.5rem" },
  footerSmallLink: { fontSize: "0.75rem", fontWeight: 500, color: "#94a3b8", textDecoration: "none" },
};

export default function LandingPage({ onStartScanning }) {
  return (
    <div style={styles.root}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={styles.logoIcon}>
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>fingerprint</span>
            </div>
            <h2 style={styles.logoText}>DeepTrace<span style={styles.logoSpan}>AI</span></h2>
          </div>
          <nav style={styles.nav}>
            {["Forensics", "API Access", "Enterprise", "Research"].map(item => (
              <a key={item} href="#" style={styles.navLink}>{item}</a>
            ))}
          </nav>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button style={styles.loginBtn}>Log In</button>
            <button style={styles.ctaBtn} onClick={onStartScanning}>Start Scanning</button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section style={{ padding: "7rem 1.5rem 6rem" }}>
        <div style={styles.hero}>
          <div style={styles.heroGrid}>
            <div>
              <div style={styles.badge}>
                <span style={styles.dot} />
                v4.0 Live: Real-time Generative Detection
              </div>
              <h1 style={styles.h1}>
                Unmask the Truth with{" "}
                <span style={styles.gradientText}>AI Forensics</span>
              </h1>
              <p style={styles.heroParagraph}>
                Protect your integrity against digital deception. Our industry-leading neural engine identifies manipulated media with 99.8% precision, verified by global intelligence standards.
              </p>
              <div style={styles.btnRow}>
                <button style={styles.analyzeBtnHero} onClick={onStartScanning}>
                  Analyze Now
                  <span className="material-symbols-outlined">arrow_forward</span>
                </button>
                <button style={styles.demoBtn}>Request Enterprise Demo</button>
              </div>
              <div style={styles.trustRow}>
                {["NIST Certified", "SOC2 Type II", "Privacy First"].map(t => (
                  <span key={t} style={styles.trustItem}>
                    <span className="material-symbols-outlined" style={styles.checkIcon}>check_circle</span>
                    {t}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <div style={styles.imageCard}>
                <div style={styles.imageInner}>
                  <div style={{ width: "100%", height: 280, backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDY2oGElVxWuxDb5nJhl43qiXX9bcn8BwQCDcIcy3VDylEH6W7fHwH4W9wiY8rjo0eWazYRXEwxz5qZtBHfQ6TMdB5bo8EwHgRXsuPPF9lHCx06H9ePoJf0VCaRCaYNUMiViKLF9VEK8j7ANBM-TptG6r1SuXMlGQZBBDfkNniMST3ADNbtfip41Hv0D4MIcWQHeXgru8Lsd09LV7XrzryysHsX_pgUJtddHwfuJ4yAhps9cMIpwLu9vNll9_rvcUDK8bJSnsTkUt8')", backgroundSize: "cover", backgroundPosition: "center", position: "relative" }}>
                    <div style={styles.scanOverlay}>
                      <div style={styles.scanBar}>
                        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                          <span className="material-symbols-outlined" style={{ color: "white" }}>scan</span>
                          <div>
                            <div style={styles.scanLabel}>Current Scan</div>
                            <div style={styles.scanName}>Source_Verification_720p.mp4</div>
                          </div>
                        </div>
                        <div style={styles.confidence}>
                          <div style={styles.scanLabel}>Confidence</div>
                          <div style={styles.confidenceVal}>99.82%</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trusted by */}
      <section style={styles.trust}>
        <div style={styles.trustInner}>
          <p style={styles.trustTitle}>Trusted by Global Media and Governments</p>
          <div style={styles.logoRow}>
            {["REUTERS", "BBC", "CNN", "ALJAZEERA", "THE NY TIMES"].map(name => (
              <span key={name} style={styles.logoName}>{name}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities */}
      <section style={styles.capabilities}>
        <div style={styles.capabilitiesInner}>
          <div style={styles.capHeader}>
            <p style={styles.capLabel}>Core Capabilities</p>
            <h2 style={styles.capH2}>Multi-Modal Verification for the Synthetics Era</h2>
            <p style={styles.capSub}>Our engine doesn't just look for glitches. It analyzes physiological signals, metadata forensics, and generative artifacts across all digital mediums.</p>
          </div>
          <div style={styles.cardsGrid}>
            {[
              { icon: "videocam", title: "Video Analysis", desc: "Frame-by-frame physiological signal detection, blink rate analysis, and facial inconsistency mapping powered by temporal consistency checks.", items: ["Heartbeat (rPPG) detection", "Lip-sync verification"] },
              { icon: "image", title: "Image Forensics", desc: "Pixel-level metadata auditing and GAN-generated artifact identification. We detect Diffusion and Transformer based generation traces.", items: ["Error Level Analysis (ELA)", "Noise profile matching"] },
              { icon: "mic", title: "Audio Authentication", desc: "Spectrogram analysis to uncover synthetic voice cloning and frequency anomalies. Detects sophisticated text-to-speech models.", items: ["Phonetical anomaly detection", "Synthetic silence signatures"] },
            ].map(({ icon, title, desc, items }) => (
              <div key={title} style={styles.card}>
                <div style={styles.cardIcon}>
                  <span className="material-symbols-outlined">{icon}</span>
                </div>
                <div>
                  <h4 style={styles.cardTitle}>{title}</h4>
                  <p style={styles.cardText}>{desc}</p>
                </div>
                <ul style={styles.cardList}>
                  {items.map(item => (
                    <li key={item} style={styles.cardListItem}>
                      <span className="material-symbols-outlined" style={styles.taskIcon}>task_alt</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section style={styles.stats}>
        <div style={styles.statsInner}>
          <div style={styles.statsGrid}>
            {[["99.8%", "Detection Accuracy"], ["< 2.4s", "Analysis Speed"], ["1.2M+", "Daily Scans"], ["24/7", "Monitoring"]].map(([num, label]) => (
              <div key={label} style={styles.statCard}>
                <div style={styles.statNum}>{num}</div>
                <div style={styles.statLabel}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={styles.cta}>
        <div style={styles.ctaInner}>
          <div style={styles.ctaDots} />
          <div style={styles.ctaContent}>
            <h2 style={styles.ctaH2}>Verify your content before it's too late.</h2>
            <p style={styles.ctaP}>Join over 5,000 organizations using DeepTrace to secure their digital communication channels and verify news sources.</p>
            <div style={styles.ctaBtnRow}>
              <button style={styles.ctaStartBtn} onClick={onStartScanning}>Get Started Free</button>
              <button style={styles.ctaExpertBtn}>Speak to an Expert</button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <div style={styles.footerInner}>
          <div style={styles.footerGrid}>
            <div style={styles.footerBrand}>
              <div style={styles.footerLogoRow}>
                <div style={styles.logoIcon}>
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>fingerprint</span>
                </div>
                <h2 style={styles.logoText}>DeepTrace<span style={styles.logoSpan}>AI</span></h2>
              </div>
              <p style={styles.footerTagline}>The definitive platform for media authentication and deepfake forensics. Protecting truth in the age of generative AI.</p>
            </div>
            <div>
              <h5 style={styles.footerHeading}>Platform</h5>
              <ul style={styles.footerList}>
                {["Video Detection", "Audio Forensics", "API Documentation", "Browser Extension"].map(i => <li key={i}><a href="#" style={styles.footerLink}>{i}</a></li>)}
              </ul>
            </div>
            <div>
              <h5 style={styles.footerHeading}>Resources</h5>
              <ul style={styles.footerList}>
                {["Case Studies", "Research Papers", "Media Kit", "Ethical AI Charter"].map(i => <li key={i}><a href="#" style={styles.footerLink}>{i}</a></li>)}
              </ul>
            </div>
            <div>
              <h5 style={styles.footerHeading}>Subscribe</h5>
              <p style={{ fontSize: "0.875rem", color: "#64748b", marginBottom: "1rem" }}>Get the latest insights on synthetic media trends.</p>
              <input type="email" placeholder="Email address" style={{ width: "100%", borderRadius: 8, border: "1px solid #e2e8f0", padding: "0.5rem 1rem", fontSize: "0.875rem", marginBottom: 8 }} />
              <button style={{ width: "100%", borderRadius: 8, backgroundColor: "#0f172a", color: "white", padding: "0.5rem", fontSize: "0.875rem", fontWeight: 700, border: "none", cursor: "pointer" }}>Subscribe</button>
            </div>
          </div>
          <div style={styles.footerBottom}>
            <p style={styles.footerCopy}>© 2024 DeepTrace AI Technologies Inc. All rights reserved.</p>
            <div style={styles.footerLinkRow}>
              {["Privacy Policy", "Terms of Service", "Cookie Settings"].map(l => <a key={l} href="#" style={styles.footerSmallLink}>{l}</a>)}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
