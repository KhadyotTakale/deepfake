import { useState } from "react";
import { Github } from "lucide-react";
import AudioDetector from "./components/AudioDetector";
import VideoDetector from "./components/VideoDetector";
import ImageDetector from "./components/ImageDetector";

const navItems = [
  { id: "video", label: "Video Scan" },
  { id: "image", label: "Image Scan" },
  { id: "audio", label: "Audio Scan" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("video");

  return (
    <div className="min-h-screen flex flex-col font-sans selection:bg-blue-100" style={{ background: "#ffffff", color: "#1f2937" }}>
      {/* Top Navbar */}
      <header className="h-[84px] px-6 lg:px-12 flex items-center justify-between border-b bg-white" style={{ borderColor: "#f3f4f6" }}>
        <div className="flex items-center gap-3 cursor-pointer">
          <span className="text-2xl font-black tracking-tight" style={{ color: "#374151" }}>
            <span className="text-blue-500">bherr</span>
          </span>
        </div>

        <nav className="hidden md:flex items-center gap-10">
          {navItems.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`text-[15px] font-semibold transition-colors ${activeTab === id ? "text-blue-500" : "text-gray-500 hover:text-gray-800"}`}
            >
              {label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          <button className="hidden sm:block px-5 py-2.5 border rounded-md text-[13px] font-bold tracking-wider hover:bg-gray-50 border-gray-300 text-gray-700 transition-all uppercase">
            API
          </button>
          <button className="hidden sm:flex items-center gap-2 px-4 py-2 hover:bg-gray-50 text-gray-700 transition-all">
            <Github size={24} />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center justify-start pt-28 pb-32 px-6 w-full relative">
        <div className="w-full max-w-[800px] mx-auto z-10 relative">
          {activeTab === "video" && <VideoDetector />}
          {activeTab === "image" && <ImageDetector />}
          {activeTab === "audio" && <AudioDetector />}
        </div>
      </main>

      {/* Dark Footer */}
      <footer className="w-full" style={{ background: "#333333", color: "#e5e7eb" }}>
        <div className="py-16 px-8 lg:px-32 grid grid-cols-1 md:grid-cols-3 gap-12 lg:gap-24 opacity-90 max-w-[1400px] mx-auto">
          <div>
            <span className="text-2xl font-black tracking-tight" style={{ color: "#ffffff" }}>
              bherr
            </span>
          </div>

          <div className="flex justify-between gap-12 md:col-span-2">
            <div className="flex flex-col gap-4 text-[13px]">
              <h4 className="font-bold text-white uppercase tracking-widest mb-2">Company</h4>
              <a href="#" className="hover:text-white transition-colors opacity-80 decoration-transparent">About Us</a>
              <a href="#" className="hover:text-white transition-colors opacity-80 decoration-transparent">Contact Us</a>
              <a href="#" className="hover:text-white transition-colors opacity-80 decoration-transparent">Blog</a>
              <a href="#" className="hover:text-white transition-colors opacity-80 decoration-transparent">FAQ</a>
            </div>

            <div className="flex flex-col gap-4 text-[13px] text-right sm:text-left">
              <h4 className="font-bold text-white uppercase tracking-widest mb-2">Where We Are</h4>
              <p className="opacity-80 leading-relaxed">India</p>
              <p className="mt-4 opacity-80">info@bherr.ai</p>

            </div>
          </div>
        </div>

        <div className="py-6 px-8 lg:px-32 flex flex-col sm:flex-row items-center justify-between text-[11px] font-medium tracking-wide uppercase" style={{ background: "#222222", color: "#9ca3af" }}>
          <p>bherr™ | © 2026</p>
          <div className="flex gap-6 mt-4 sm:mt-0">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Release Notes</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
