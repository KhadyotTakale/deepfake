import { useState, useRef } from "react";
import { Upload, X, Video } from "lucide-react";
import { detectVideo } from "../api";
import ResultCard from "./ResultCard";

export default function VideoDetector() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef(null);

    const handleFile = (f) => {
        if (!f) return;
        if (!f.type.startsWith("video/")) { setError("Please upload a video file."); return; }
        if (f.size > 100 * 1024 * 1024) { setError("Video too large (max 100 MB)."); return; }
        setError(""); setFile(f); setResult(null);
        setPreview(URL.createObjectURL(f));
    };

    const handleDragOver = (e) => { e.preventDefault(); setDragActive(true); };
    const handleDragLeave = () => setDragActive(false);
    const handleDrop = (e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); };
    const clear = () => { if (preview) URL.revokeObjectURL(preview); setFile(null); setPreview(null); setResult(null); setError(""); };

    const handleAnalyze = async () => {
        if (!file) { setError("Please upload a video first."); return; }
        setError(""); setResult(null); setLoading(true);
        try {
            const data = await detectVideo(file);
            setResult(data);
        } catch (e) {
            setError(e.message || "Analysis failed.");
        } finally { setLoading(false); }
    };

    return (
        <div className="w-full fade-in">
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 lg:gap-12">
                {/* Left Column (Main Action) */}
                <div className="xl:col-span-2 flex flex-col gap-6">
                    <div className="card p-8 md:p-10">
                        <h2 className="text-lg font-bold mb-6" style={{ color: "var(--color-text-heading)" }}>Upload Video to Analyze</h2>

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
                                    Drag & drop a video here, or click to browse
                                </p>
                                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>MP4, AVI, MOV • Max 100 MB</p>
                                <input ref={inputRef} type="file" accept="video/*" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
                            </div>
                        ) : (
                            <div className="border rounded-2xl overflow-hidden" style={{ borderColor: "var(--color-border)" }}>
                                <div className="relative">
                                    <video src={preview} controls className="w-full max-h-[500px]" style={{ background: "#000" }} />
                                    <button onClick={clear}
                                        className="absolute top-4 right-4 w-9 h-9 rounded-full flex items-center justify-center cursor-pointer hover:scale-105 transition-transform"
                                        style={{ background: "rgba(0,0,0,0.6)", color: "#fff" }}>
                                        <X size={16} />
                                    </button>
                                </div>
                                <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4" style={{ borderTop: "1px solid var(--color-border-light)" }}>
                                    <div className="flex items-center gap-3 overflow-hidden">
                                        <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" style={{ background: "var(--color-primary-lighter)", color: "var(--color-primary)" }}>
                                            <Video size={20} />
                                        </div>
                                        <span className="text-base font-medium truncate" style={{ color: "var(--color-text-body)" }}>{file.name}</span>
                                    </div>
                                    <button onClick={handleAnalyze} disabled={loading} className="btn-primary w-full sm:w-auto justify-center shrink-0">
                                        {loading ? "Processing..." : "Analyze Video"}
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

                    <ResultCard result={result} loading={loading} />
                </div>

                {/* Right Column (Info Sidebar) */}
                <div className="flex flex-col gap-6">
                    <div className="card p-8 md:p-10">
                        <h2 className="text-base font-bold mb-6" style={{ color: "var(--color-text-heading)" }}>About This Tool</h2>
                        <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-light)" }}>
                            Upload a video to run our EfficientNet-B4 + LSTM deepfake detection model. The AI analyzes spatial features
                            (frame artifacts) and temporal features (movement/flicker) to spot deepfakes.
                        </p>
                    </div>

                    <div className="card p-8 md:p-10">
                        <h3 className="text-sm font-bold mb-6 uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>What We Check</h3>
                        <ul className="space-y-3 text-sm font-medium" style={{ color: "var(--color-text-body)" }}>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Face Tracking</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Temporal Jitter</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Lip Sync Accuracy</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Compression Artifacts</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
