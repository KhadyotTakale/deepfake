import { useState } from "react";
import AudioDetector from "./components/AudioDetector";
import ImageDetector from "./components/ImageDetector";
import LandingPage from "./components/LandingPage";
import VideoScanPage from "./components/VideoScanPage";

export default function App() {
  const [activeTab, setActiveTab] = useState("landing");

  const navigate = (tab) => setActiveTab(tab);

  if (activeTab === "landing") {
    return (
      <LandingPage
        onStartScanning={() => navigate("video")}
        onNavigate={navigate}
      />
    );
  }

  if (activeTab === "video") {
    return <VideoScanPage onNavigate={navigate} />;
  }

  // image / audio fall back to existing detectors wrapped in a light nav shell
  return (
    <div style={{ backgroundColor: "#f6f6f8", minHeight: "100vh", fontFamily: "'Inter', sans-serif" }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid #e2e4ed", backgroundColor: "white", padding: "0.75rem 2.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 32, height: 32, backgroundColor: "#193ce6", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", color: "white" }}>
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>shield_with_heart</span>
          </div>
          <h2 style={{ fontSize: "1.125rem", fontWeight: 700, color: "#0f172a", margin: 0 }}>AI Forensics</h2>
        </div>
        <nav style={{ display: "flex", gap: "1.5rem" }}>
          {[
            { tab: "landing", label: "Home" },
            { tab: "video", label: "Video Scan" },
            { tab: "image", label: "Image Scan" },
            { tab: "audio", label: "Audio Scan" },
          ].map(({ tab, label }) => (
            <button
              key={tab}
              onClick={() => navigate(tab)}
              style={{
                fontSize: "0.875rem",
                fontWeight: activeTab === tab ? 700 : 500,
                color: activeTab === tab ? "#193ce6" : "#475569",
                background: "none",
                border: "none",
                borderBottom: activeTab === tab ? "2px solid #193ce6" : "2px solid transparent",
                cursor: "pointer",
                padding: "0.25rem 0 0.5rem",
              }}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>
      <main style={{ maxWidth: "72rem", margin: "0 auto", padding: "2.5rem" }}>
        {activeTab === "image" && <ImageDetector />}
        {activeTab === "audio" && <AudioDetector />}
      </main>
    </div>
  );
}
