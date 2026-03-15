import { useState, useRef } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import { detectImage } from "../api";
import ResultCard from "./ResultCard"; 

export default function ImageDetector() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);
    const [error, setError] = useState("");
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef(null);
    const timerRef = useRef(null);
 
    const handleFile = (f) => {
        if (!f) return;
        if (!f.type.startsWith("image/")) { setError("Please upload an image file."); return; }
        if (f.size > 20 * 1024 * 1024) { setError("Image too large (max 20 MB)."); return; }
        setError(""); setFile(f); setResult(null);
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(f);
    };

    const handleDragOver = (e) => { e.preventDefault(); setDragActive(true); };
    const handleDragLeave = () => setDragActive(false);
    const handleDrop = (e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); };
    const clear = () => { setFile(null); setPreview(null); setResult(null); setError(""); setElapsedTime(0); };

    const handleAnalyze = async () => {
        if (!file) { setError("Please upload an image first."); return; }
        setError(""); setResult(null); setLoading(true); setElapsedTime(0);

        const startTime = Date.now();
        timerRef.current = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
        try {
            const data = await detectImage(file);
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
                    <div className="card-glass border border-white/10 p-10 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-3xl rounded-full" />
                        <h2 className="text-xl font-black mb-8 text-white tracking-tight flex items-center gap-3">
                            <ImageIcon className="text-indigo-400" size={24} />
                            Image Forensic Scan
                        </h2>

                        {!file ? (
                            <div
                                className={`dropzone relative z-10 border-2 border-dashed transition-all duration-300 ${
                                    dragActive 
                                    ? "border-indigo-500 bg-indigo-500/10 shadow-[0_0_30px_rgba(99,102,241,0.1)]" 
                                    : "border-white/10 bg-white/5 hover:border-white/20"
                                } rounded-3xl p-16 text-center cursor-pointer group/zone`}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                onClick={() => inputRef.current?.click()}
                            >
                                <div className="w-20 h-20 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-6 group-hover/zone:scale-110 group-hover/zone:bg-indigo-500/10 transition-all">
                                    <Upload size={32} className="text-gray-400 group-hover/zone:text-indigo-400" />
                                </div>
                                <p className="text-lg font-bold text-white mb-2">
                                    Drop your image <span className="text-indigo-400">here</span>
                                </p>
                                <p className="text-sm text-gray-500">
                                    JPEG, PNG, WebP up to 20MB
                                </p>
                                <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
                            </div>
                        ) : (
                            <div className="border border-white/10 rounded-3xl overflow-hidden bg-black/40 backdrop-blur-sm relative z-10">
                                <div className="relative group/img">
                                    <img src={preview} alt="Preview" className="w-full max-h-[500px] object-contain" />
                                    <button onClick={clear}
                                        className="absolute top-6 right-6 w-10 h-10 rounded-full flex items-center justify-center cursor-pointer bg-black/60 text-white hover:bg-rose-500 transition-all opacity-0 group-hover/img:opacity-100 backdrop-blur-md">
                                        <X size={18} />
                                    </button>
                                </div>
                                <div className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-6 bg-white/5">
                                    <div className="flex items-center gap-4 overflow-hidden">
                                        <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center shrink-0 border border-indigo-500/20">
                                            <ImageIcon className="text-indigo-400" size={24} />
                                        </div>
                                        <div>
                                            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Source File</p>
                                            <span className="text-sm font-bold text-white truncate block max-w-[200px]">{file.name}</span>
                                        </div>
                                    </div>
                                    <button 
                                        onClick={handleAnalyze} 
                                        disabled={loading} 
                                        className={`px-8 py-4 rounded-xl font-black text-xs uppercase tracking-[0.2em] transition-all flex items-center gap-3 ${
                                            loading 
                                            ? "bg-gray-800 text-gray-500 cursor-not-allowed" 
                                            : "bg-indigo-600 text-white hover:bg-indigo-500 hover:shadow-lg hover:shadow-indigo-500/30 hover:-translate-y-1"
                                        }`}
                                    >
                                        {loading ? (
                                            <>
                                                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                                Scanning...
                                            </>
                                        ) : "Initialize Scan"}
                                    </button>
                                </div>
                            </div>
                        )}

                        {error && (
                            <div className="mt-6 rounded-2xl p-5 border border-rose-500/20 bg-rose-500/10 text-sm font-bold text-rose-400 flex items-center gap-3">
                                <X size={18} className="shrink-0" />
                                {error}
                            </div>
                        )}
                    </div>

                    <ResultCard result={result} loading={loading} duration={elapsedTime} />
                </div>

                {/* Right Column (Info Sidebar) */}
                <div className="flex flex-col gap-6">
                    <div className="card p-8 md:p-10">
                        <h2 className="text-base font-bold mb-6" style={{ color: "var(--color-text-heading)" }}>About This Tool</h2>
                        <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-light)" }}>
                            Upload any image to check for signs of AI generation or digital manipulation. The AI will analyze lighting,
                            inconsistencies, facial features, and background artifacts.
                        </p>
                    </div>

                    <div className="card p-8 md:p-10">
                        <h3 className="text-sm font-bold mb-6 uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>What We Check</h3>
                        <ul className="space-y-3 text-sm font-medium" style={{ color: "var(--color-text-body)" }}>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Lighting & Shadows</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> AI Artifacts</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Edge Consistency</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Face & Hands Detail</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
