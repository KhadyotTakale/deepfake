import { useState } from "react";
import AudioScanPage from "./components/AudioScanPage";
import ImageScanPage from "./components/ImageScanPage";
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

  if (activeTab === "image") {
    return <ImageScanPage onNavigate={navigate} />;
  }

  if (activeTab === "audio") {
    return <AudioScanPage onNavigate={navigate} />;
  }

  return (
    <div style={{ padding: "2rem", color: "#64748b" }}>
      Tab not found. <button onClick={() => navigate("landing")}>Go Home</button>
    </div>
  );
}
