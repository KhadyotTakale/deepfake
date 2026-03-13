import { useState, useRef } from "react";
import { Upload, X, Mic } from "lucide-react";
import { detectAudio } from "../api";
import ResultCard from "./ResultCard";

export default function AudioDetector() {
    const [file, setFile] = useState(null);
    const [audioUrl, setAudioUrl] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);
    const [error, setError] = useState("");
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef(null);
    const timerRef = useRef(null);

    const handleFile = (f) => {
        if (!f) return;
        if (!f.type.startsWith("audio/")) { 
            setError("Please upload an audio file (MP3, WAV, etc.)."); 
            return; 
        }
        if (f.size > 20 * 1024 * 1024) { 
            setError("Audio file too large (max 20 MB)."); 
            return; 
        }
        setError(""); 
        setFile(f); 
        setResult(null);
        setAudioUrl(URL.createObjectURL(f));
    };

    const handleDragOver = (e) => { e.preventDefault(); setDragActive(true); };
    const handleDragLeave = () => setDragActive(false);
    const handleDrop = (e) => { 
        e.preventDefault(); 
        setDragActive(false); 
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); 
    };
    const clear = () => { 
        if (audioUrl) URL.revokeObjectURL(audioUrl);
        setFile(null); 
        setAudioUrl(null); 
        setResult(null); 
        setError(""); 
        setElapsedTime(0);
    };

    const handleAnalyze = async () => {
        if (!file) { setError("Please upload an audio file first."); return; }
        setError(""); setResult(null); setLoading(true); setElapsedTime(0);

        const startTime = Date.now();
        timerRef.current = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
        try {
            const data = await detectAudio(file);
            setResult(data);
        } catch (e) {
            setError(e.message || "Analysis failed.");
        } finally { 
            if (timerRef.current) clearInterval(timerRef.current);
            setLoading(false); 
        }
    };

    return (
        <div className="w-full fade-in">
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 lg:gap-12">
                {/* Left Column (Main Action) */}
                <div className="xl:col-span-2 flex flex-col gap-6">
                    <div className="card p-8 md:p-10">
                        <h2 className="text-lg font-bold mb-6" style={{ color: "var(--color-text-heading)" }}>Upload Audio to Analyze</h2>

                        {!file ? (
                            <div
                                className={`dropzone ${dragActive ? "active" : ""}`}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                onClick={() => inputRef.current?.click()}
                            >
                                <Upload size={48} style={{ color: "var(--color-text-muted)", marginBottom: "1.25rem" }} className="mx-auto" />
                                <p className="text-base font-medium mb-2" style={{ color: "var(--color-text-body)" }}>
                                    Drag & drop an audio file here, or click to browse
                                </p>
                                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>MP3, WAV, M4A • Max 20 MB</p>
                                <input ref={inputRef} type="file" accept="audio/*" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
                            </div>
                        ) : (
                            <div className="border rounded-2xl overflow-hidden" style={{ borderColor: "var(--color-border)" }}>
                                <div className="p-10 flex flex-col items-center justify-center bg-gray-50 relative">
                                    <div className="w-20 h-20 rounded-full flex items-center justify-center mb-6" style={{ background: "var(--color-primary-lighter)", color: "var(--color-primary)" }}>
                                        <Mic size={40} />
                                    </div>
                                    <audio src={audioUrl} controls className="w-full max-w-md" />
                                    <button onClick={clear}
                                        className="absolute top-4 right-4 w-9 h-9 rounded-full flex items-center justify-center cursor-pointer hover:scale-105 transition-transform"
                                        style={{ background: "rgba(0,0,0,0.1)", color: "var(--color-text-muted)" }}>
                                        <X size={16} />
                                    </button>
                                </div>
                                <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4" style={{ borderTop: "1px solid var(--color-border-light)" }}>
                                    <div className="flex items-center gap-3 overflow-hidden">
                                        <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" style={{ background: "var(--color-primary-lighter)", color: "var(--color-primary)" }}>
                                            <Mic size={20} />
                                        </div>
                                        <span className="text-base font-medium truncate" style={{ color: "var(--color-text-body)" }}>{file.name}</span>
                                    </div>
                                    <button onClick={handleAnalyze} disabled={loading} className="btn-primary w-full sm:w-auto justify-center shrink-0">
                                        {loading ? "Analyzing..." : "Analyze Audio"}
                                    </button>
                                </div>
                            </div>
                        )}

                        {error && (
                            <div className="mt-5 rounded-xl p-4 text-sm font-medium" style={{ background: "var(--color-danger-bg)", color: "var(--color-danger)" }}>
                                {error}
                            </div>
                        )}
                    </div>

                    <ResultCard result={result} loading={loading} duration={elapsedTime} />
                </div>

                {/* Right Column (Info Sidebar) */}
                <div className="flex flex-col gap-6">
                    <div className="card p-8 md:p-10">
                        <h2 className="text-base font-bold mb-6" style={{ color: "var(--color-text-heading)" }}>About Audio Forensics</h2>
                        <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-light)" }}>
                            Upload audio clips to detect speech synthesis or voice cloning. The system analyzes spectral patterns, 
                            natural breathing intervals, and digital artifacts indicative of AI generation.
                        </p>
                    </div>

                    <div className="card p-8 md:p-10">
                        <h3 className="text-sm font-bold mb-6 uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Forensic Checks</h3>
                        <ul className="space-y-3 text-sm font-medium" style={{ color: "var(--color-text-body)" }}>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Voice Cadence & Rhythm</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Spectral Signal Analysis</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Synthetic Breathing Patterns</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Environmental Ambiance</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Digital Signal Noise</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
