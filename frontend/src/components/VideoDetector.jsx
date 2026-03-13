import { useState, useRef } from "react";
import { Upload, X, Video, Layers } from "lucide-react";
import { detectVideoDetailed } from "../api";
import ResultCard from "./ResultCard";
import ForensicPanel from "./ForensicPanel";

export default function VideoDetector() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [detailedData, setDetailedData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);
    const [error, setError] = useState("");
    const [dragActive, setDragActive] = useState(false);
    const [pipelineStage, setPipelineStage] = useState("");
    const inputRef = useRef(null);
    const timerRef = useRef(null);

    const handleFile = (f) => {
        if (!f) return;
        if (!f.type.startsWith("video/")) { setError("Please upload a video file."); return; }
        if (f.size > 100 * 1024 * 1024) { setError("Video too large (max 100 MB)."); return; }
        setError(""); setFile(f); setResult(null); setDetailedData(null);
        setPreview(URL.createObjectURL(f));
    };

    const handleDragOver = (e) => { e.preventDefault(); setDragActive(true); };
    const handleDragLeave = () => setDragActive(false);
    const handleDrop = (e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); };
    const clear = () => { if (preview) URL.revokeObjectURL(preview); setFile(null); setPreview(null); setResult(null); setDetailedData(null); setError(""); setPipelineStage(""); setElapsedTime(0); };

    const handleAnalyze = async () => {
        if (!file) { setError("Please upload a video first."); return; }
        setError(""); setResult(null); setDetailedData(null); setLoading(true); setElapsedTime(0);

        // Start duration timer
        const startTime = Date.now();
        timerRef.current = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);

        // Simulate pipeline stage indicators
        const stages = [
            "Extracting frames...",
            "Running CNN model...",
            "Extracting forensic features...",
            "Building knowledge graph...",
            "Querying forensic knowledge base...",
            "LLM reasoning analysis...",
            "Computing consensus verdict...",
        ];
        let stageIdx = 0;
        setPipelineStage(stages[0]);
        const interval = setInterval(() => {
            stageIdx++;
            if (stageIdx < stages.length) {
                setPipelineStage(stages[stageIdx]);
            }
        }, 2500);

        try {
            const data = await detectVideoDetailed(file);
            setResult({
                verdict: data.verdict,
                confidence: data.confidence,
                reasons: data.reasons,
                summary: data.summary,
            });
            setDetailedData(data);
        } catch (e) {
            setError(e.message || "Analysis failed.");
        } finally {
            clearInterval(interval);
            if (timerRef.current) clearInterval(timerRef.current);
            setPipelineStage("");
            setLoading(false);
        }
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

                        {/* Pipeline stage indicator */}
                        {loading && pipelineStage && (
                            <div className="mt-5 pipeline-stage-card fade-in">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="inline-block w-5 h-5 border-2 rounded-full spinner"
                                            style={{ borderColor: "var(--color-primary-lighter)", borderTopColor: "var(--color-primary)" }} />
                                        <span className="text-sm font-medium" style={{ color: "var(--color-primary)" }}>
                                            {pipelineStage}
                                        </span>
                                    </div>
                                    <div className="text-sm font-mono font-bold px-3 py-1 rounded-bg" style={{ background: "rgba(124, 58, 237, 0.1)", color: "var(--color-primary)" }}>
                                        {Math.floor(elapsedTime / 60)}:{(elapsedTime % 60).toString().padStart(2, '0')}
                                    </div>
                                </div>
                                <div className="pipeline-dots mt-3">
                                    <span className="pipeline-dot active" />
                                    <span className="pipeline-dot-line" />
                                    <span className="pipeline-dot active" />
                                    <span className="pipeline-dot-line" />
                                    <span className="pipeline-dot active" />
                                    <span className="pipeline-dot-line" />
                                    <span className="pipeline-dot" />
                                    <span className="pipeline-dot-line" />
                                    <span className="pipeline-dot" />
                                    <span className="pipeline-dot-line" />
                                    <span className="pipeline-dot" />
                                    <span className="pipeline-dot-line" />
                                    <span className="pipeline-dot" />
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

                    {/* Detailed Forensic Panel (only for video) */}
                    <ForensicPanel data={detailedData} />
                </div>

                {/* Right Column (Info Sidebar) */}
                <div className="flex flex-col gap-6">
                    <div className="card p-8 md:p-10">
                        <h2 className="text-base font-bold mb-6" style={{ color: "var(--color-text-heading)" }}>About This Tool</h2>
                        <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-light)" }}>
                            Upload a video to run our <strong>advanced multi-stage forensic pipeline</strong>. The system combines CNN deep learning,
                            signal processing, knowledge graph analysis, and LLM reasoning to detect deepfakes with high precision.
                        </p>
                    </div>

                    <div className="card p-8 md:p-10">
                        <h3 className="text-sm font-bold mb-6 uppercase tracking-wider flex items-center gap-2" style={{ color: "var(--color-text-muted)" }}>
                            <Layers size={14} />
                            Pipeline Stages
                        </h3>
                        <ul className="space-y-3 text-sm font-medium" style={{ color: "var(--color-text-body)" }}>
                            <li className="flex items-center gap-3"><span className="text-purple-500">①</span> CNN Detection <span className="text-xs ml-auto" style={{ color: "var(--color-text-muted)" }}>EfficientNet + Attention-GRU</span></li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">②</span> Feature Extraction <span className="text-xs ml-auto" style={{ color: "var(--color-text-muted)" }}>9 forensic signals</span></li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">③</span> Graph Building <span className="text-xs ml-auto" style={{ color: "var(--color-text-muted)" }}>NetworkX</span></li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">④</span> GraphRAG Retrieval <span className="text-xs ml-auto" style={{ color: "var(--color-text-muted)" }}>Knowledge base</span></li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">⑤</span> LLM Reasoning <span className="text-xs ml-auto" style={{ color: "var(--color-text-muted)" }}>GPT-4o-mini</span></li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">⑥</span> Consensus Engine <span className="text-xs ml-auto" style={{ color: "var(--color-text-muted)" }}>Ensemble</span></li>
                        </ul>
                    </div>

                    <div className="card p-8 md:p-10">
                        <h3 className="text-sm font-bold mb-6 uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Forensic Signals</h3>
                        <ul className="space-y-3 text-sm font-medium" style={{ color: "var(--color-text-body)" }}>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> GAN Noise Fingerprint</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Face Boundary Blending</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Temporal Consistency</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Lip-Sync Accuracy</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Eye Blink Patterns</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Lighting & BG Analysis</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Spectral Artifacts</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Texture Perfection</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
