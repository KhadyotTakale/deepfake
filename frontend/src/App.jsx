import { useState } from "react";
import { Github } from "lucide-react";
import AudioDetector from "./components/AudioDetector";
import VideoDetector from "./components/VideoDetector";
import ImageDetector from "./components/ImageDetector";
import HistoryPage from "./components/HistoryPage";

const navItems = [
  { id: "video", label: "Video Scan" },
  { id: "image", label: "Image Scan" },
  { id: "audio", label: "Audio Scan" },
  { id: "history", label: "History" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("video");

  return (
    <div className="min-h-screen flex flex-col font-sans selection:bg-indigo-500/30 bg-[#080c14] text-gray-300">
      {/* Top Navbar */}
      <header className="h-[84px] px-6 lg:px-12 flex items-center justify-between border-b border-white/5 bg-[#080c14]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform">
            <span className="text-white font-black text-xl">B</span>
          </div>
          <span className="text-2xl font-black tracking-tight text-white">
            bherr<span className="text-indigo-400">.ai</span>
          </span>
        </div>

        <nav className="hidden md:flex items-center gap-10">
          {navItems.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`text-[14px] font-bold uppercase tracking-widest transition-all relative py-2 ${activeTab === id ? "text-white" : "text-gray-500 hover:text-gray-300"}`}
            >
              {label}
              {activeTab === id && (
                <span className="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.6)]" />
              )}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-6">
          <button className="hidden sm:block text-[13px] font-bold tracking-widest text-gray-400 hover:text-white transition-colors uppercase">
            Documentation
          </button>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="p-2 text-gray-400 hover:text-white transition-all hover:scale-110">
            <Github size={22} />
          </a>
          <button className="px-6 py-2.5 rounded-full bg-white text-black text-xs font-black uppercase tracking-widest hover:bg-gray-200 transition-all shadow-xl shadow-white/5">
            Get Pro
          </button>
        </div>
      </header>

      {/* Hero Section Background Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-[1200px] h-[500px] pointer-events-none">
        <div className="absolute top-[-100px] left-1/4 w-[400px] h-[400px] bg-indigo-600/10 rounded-full blur-[120px]" />
        <div className="absolute top-[50px] right-1/4 w-[400px] h-[400px] bg-cyan-600/10 rounded-full blur-[120px]" />
      </div>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center justify-start pt-20 pb-32 px-6 w-full relative z-10">
        <div className="text-center mb-16 max-w-2xl">
          <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-white mb-6">
            AI Content <span className="text-gradient">Forensics</span>
          </h1>
          <p className="text-lg text-gray-400 leading-relaxed">
            Detect deepfakes and AI-generated content with state-of-the-art forensic analysis. 
            Trusted by media professionals worldwide.
          </p>
        </div>

        <div className="w-full max-w-[900px] mx-auto">
          {activeTab === "video" && <VideoDetector />}
          {activeTab === "image" && <ImageDetector />}
          {activeTab === "audio" && <AudioDetector />}
          {activeTab === "history" && <HistoryPage />}
        </div>
      </main>

      {/* Dark Footer */}
      <footer className="w-full border-t border-white/5 bg-[#05070a]">
        <div className="max-w-[1400px] mx-auto py-20 px-12 grid grid-cols-1 md:grid-cols-4 gap-16">
          <div className="col-span-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
                <span className="text-white font-black text-base">B</span>
              </div>
              <span className="text-xl font-bold text-white tracking-tight">bherr.ai</span>
            </div>
            <p className="text-sm text-gray-500 leading-relaxed">
              Advancing digital trust through cutting-edge AI detection and media authentication technology.
            </p>
          </div>

          <div className="flex flex-col gap-4">
            <h4 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-2">Capabilities</h4>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">Video Forensics</a>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">Voice Cloning Detection</a>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">Image Provenance</a>
          </div>

          <div className="flex flex-col gap-4">
            <h4 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-2">Resources</h4>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">Research Paper</a>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">API Docs</a>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">Status</a>
          </div>

          <div className="flex flex-col gap-4">
            <h4 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-2">Legal</h4>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">Privacy</a>
            <a href="#" className="text-sm text-gray-500 hover:text-indigo-400 transition-colors">Terms</a>
          </div>
        </div>

        <div className="py-8 px-12 flex flex-col sm:flex-row items-center justify-between border-t border-white/5 text-[10px] font-bold tracking-[0.3em] uppercase text-gray-600">
          <p>© 2026 BHERR LABS. ALL RIGHTS RESERVED.</p>
          <div className="flex gap-8 mt-4 sm:mt-0">
            <a href="#" className="hover:text-white transition-colors">Twitter</a>
            <a href="#" className="hover:text-white transition-colors">LinkedIn</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
