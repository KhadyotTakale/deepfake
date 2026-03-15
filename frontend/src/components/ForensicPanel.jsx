import { useState } from "react";
import { Activity, Brain, GitBranch, Cpu, Zap } from "lucide-react";

// Human-friendly feature labels and descriptions
const FEATURE_META = {
    gan_noise: { label: "GAN Fingerprint", icon: "🔬", color: "#6366f1" },
    face_blending: { label: "Spatial Blending", icon: "🎭", color: "#f43f5e" },
    temporal_jump: { label: "Motion Flux", icon: "⏱️", color: "#f59e0b" },
    lip_sync_error: { label: "Lip Synthesis", icon: "👄", color: "#ef4444" },
    eye_blink_anomaly: { label: "Biological Trace", icon: "👁️", color: "#06b6d4" },
    lighting_inconsistency: { label: "Photometric Error", icon: "💡", color: "#f97316" },
    background_coherence: { label: "Environment Gap", icon: "🖼️", color: "#10b981" },
    spectral_artifact: { label: "Spectral Leakage", icon: "📡", color: "#818cf8" },
    texture_perfection: { label: "Surface Detail", icon: "🧖", color: "#ec4899" },
};

function SegmentedPie({ features }) {
    const [hovered, setHovered] = useState(null);
    const featureEntries = Object.entries(features).filter(([, score]) => score > 0);
    
    if (featureEntries.length === 0) return (
        <div className="flex flex-col items-center justify-center p-10 opacity-50">
            <span className="text-sm font-bold uppercase tracking-widest">No Artifacts Detected</span>
        </div>
    );

    const totalScore = featureEntries.reduce((sum, [, s]) => sum + s, 0);
    const size = 260;
    const radius = size / 4;
    const strokeWidth = size / 2;
    const circumference = radius * 2 * Math.PI;

    let currentOffset = 0;

    return (
        <div className="flex flex-col lg:flex-row items-center justify-center gap-8 lg:gap-16 p-8 bg-black/20 rounded-[3rem] border border-white/5 overflow-visible relative shadow-2xl">
            <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 blur-[120px] rounded-full -mr-40 -mt-40 pointer-events-none" />
            
            <div className="relative group p-4 shrink-0">
                <svg width={size} height={size} className="transform -rotate-90 filter drop-shadow-[0_0_30px_rgba(99,102,241,0.15)] overflow-visible">
                    {featureEntries.map(([name, score]) => {
                        const meta = FEATURE_META[name] || { color: "#6b7280" };
                        const weight = (score / totalScore);
                        const segmentLength = weight * circumference;
                        const dashOffset = -currentOffset;
                        currentOffset += segmentLength;
                        const isHovered = hovered === name;

                        return (
                            <circle
                                key={name}
                                cx={size / 2}
                                cy={size / 2}
                                r={radius}
                                stroke={meta.color}
                                strokeWidth={strokeWidth}
                                strokeDasharray={`${segmentLength} ${circumference - segmentLength}`}
                                strokeDashoffset={dashOffset}
                                fill="transparent"
                                onMouseEnter={() => setHovered(name)}
                                onMouseLeave={() => setHovered(null)}
                                className="transition-all duration-500 cursor-pointer"
                                style={{ 
                                    strokeLinecap: 'butt',
                                    opacity: hovered ? (isHovered ? 1 : 0.3) : 0.85,
                                    transform: isHovered ? 'scale(1.08)' : 'scale(1)',
                                    transformOrigin: 'center'
                                }}
                            />
                        );
                    })}
                </svg>

                {/* Dynamic labels in center */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-10">
                    <div className={`flex flex-col items-center transition-all duration-500 ${hovered ? 'scale-110 opacity-100' : 'opacity-100'}`}>
                        {hovered ? (
                            <>
                                <span className="text-2xl mb-2 drop-shadow-md">{FEATURE_META[hovered]?.icon}</span>
                                <span className="text-[10px] font-black uppercase tracking-[0.3em] text-[#ccff00] mb-1 drop-shadow-[0_0_8px_rgba(204,255,0,0.5)]">
                                    {FEATURE_META[hovered]?.label}
                                </span>
                                <span className="text-5xl font-black text-white drop-shadow-2xl">
                                    {Math.round((features[hovered] / totalScore) * 100)}%
                                </span>
                            </>
                        ) : (
                            <>
                                <span className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-2">Analysis Hub</span>
                                <span className="text-5xl font-black text-[#ccff00] drop-shadow-[0_0_15px_rgba(204,255,0,0.4)]">100%</span>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Legend - Tighter Vertical List */}
            <div className="flex flex-col gap-4 min-w-[240px] max-w-[320px]">
                {featureEntries.map(([name, score]) => {
                    const meta = FEATURE_META[name] || { label: name, icon: "📊", color: "#6b7280" };
                    const weight = Math.round((score / totalScore) * 100);
                    const isHovered = hovered === name;

                    return (
                        <div 
                            key={name} 
                            onMouseEnter={() => setHovered(name)}
                            onMouseLeave={() => setHovered(null)}
                            className={`flex items-center gap-4 transition-all duration-300 ${isHovered ? 'translate-x-2' : ''}`}
                        >
                            <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: meta.color, boxShadow: `0 0 10px ${meta.color}44` }} />
                            <div className="flex-1 flex items-center justify-between group">
                                <div className="flex flex-col">
                                    <span className={`text-[10px] font-black uppercase tracking-widest transition-colors ${isHovered ? 'text-white' : 'text-gray-500'}`}>
                                        {meta.label}
                                    </span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="h-1 w-20 bg-white/5 rounded-full overflow-hidden hidden sm:block">
                                        <div className="h-full transition-all duration-1000" style={{ width: `${weight}%`, background: meta.color }} />
                                    </div>
                                    <span className="text-[10px] font-mono font-black text-white bg-white/10 px-2 py-0.5 rounded">
                                        {weight}%
                                    </span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function PipelineScoreCard({ label, score, icon, color }) {
    const pct = Math.round(score * 100);
    return (
        <div className="p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-indigo-500/30 transition-all group">
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-white/5 text-gray-400 group-hover:text-indigo-400 transition-colors">
                    {icon}
                </div>
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">
                    {label}
                </span>
            </div>
            <div className="text-3xl font-black text-white mb-4">{pct}%</div>
            <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-1000" style={{ width: `${pct}%`, background: color }} />
            </div>
        </div>
    );
}

export default function ForensicPanel({ data }) {
    if (!data) return null;

    const features = data.forensic_features?.features || {};
    const pipeline = data.pipeline_scores || {};
    const graphAnalysis = data.graph_analysis || {};
    const llmReasoning = data.llm_reasoning || {};

    return (
        <div className="space-y-16 fade-in pb-20">

            {/* ── Pipeline Scores ── */}
            {pipeline.cnn_score !== undefined && (
                <div className="card p-7">
                    <h3 className="text-xs font-bold uppercase tracking-wider mb-5 flex items-center gap-2"
                        style={{ color: "var(--color-text-muted)" }}>
                        <Zap size={14} />
                        Pipeline Ensemble Scores
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <PipelineScoreCard
                            label="CNN Model"
                            score={pipeline.cnn_score}
                            icon={<Cpu size={14} style={{ color: "#8b5cf6" }} />}
                            color="#8b5cf6"
                        />
                        <PipelineScoreCard
                            label="Graph Analysis"
                            score={pipeline.graph_score}
                            icon={<GitBranch size={14} style={{ color: "#06b6d4" }} />}
                            color="#06b6d4"
                        />
                        <PipelineScoreCard
                            label="LLM Reasoning"
                            score={pipeline.llm_score}
                            icon={<Brain size={14} style={{ color: "#f59e0b" }} />}
                            color="#f59e0b"
                        />
                    </div>

                    {/* Final Score Bar */}
                    {pipeline.final_score !== undefined && (
                        <div className="mt-5 pt-5" style={{ borderTop: "1px solid var(--color-border-light)" }}>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-bold" style={{ color: "var(--color-text-heading)" }}>
                                    Ensemble Score
                                </span>
                                <span className="text-lg font-black" style={{
                                    color: pipeline.final_score > 0.7 ? "var(--color-danger)"
                                        : pipeline.final_score < 0.3 ? "var(--color-success)"
                                            : "var(--color-warning)",
                                }}>
                                    {Math.round(pipeline.final_score * 100)}%
                                </span>
                            </div>
                            <div className="feature-bar-track" style={{ height: "8px" }}>
                                <div
                                    className="feature-bar-fill"
                                    style={{
                                        width: `${Math.round(pipeline.final_score * 100)}%`,
                                        background: pipeline.final_score > 0.7
                                            ? "linear-gradient(90deg, #ef4444, #dc2626)"
                                            : pipeline.final_score < 0.3
                                                ? "linear-gradient(90deg, #10b981, #059669)"
                                                : "linear-gradient(90deg, #f59e0b, #d97706)",
                                        height: "8px",
                                    }}
                                />
                            </div>
                            {pipeline.weights && (
                                <p className="text-xs mt-2" style={{ color: "var(--color-text-muted)" }}>
                                    Weights: CNN {Math.round(pipeline.weights.cnn * 100)}% ·
                                    Graph {Math.round(pipeline.weights.graph * 100)}% ·
                                    LLM {Math.round(pipeline.weights.llm * 100)}%
                                </p>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* ── Forensic Features ── */}
            {Object.keys(features).length > 0 && (
                <div className="card p-10 bg-white/[0.01] border border-white/5 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />
                    <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-gray-500 flex items-center gap-4 mb-12 px-2">
                        <Activity size={14} className="text-indigo-400" />
                        Forensic Feature Analysis Hub
                    </h3>
                    <SegmentedPie features={features} />
                </div>
            )}

            {/* ── Knowledge Graph Analysis ── */}
            {(graphAnalysis.artifacts?.length > 0 || graphAnalysis.inferences?.length > 0) && (
                <div className="card-glass border border-white/10 p-16 relative overflow-visible rounded-[3rem]">
                    <div className="flex items-center gap-8 mb-20 relative">
                        <div className="w-16 h-16 rounded-3xl bg-cyan-500/10 flex items-center justify-center border border-cyan-500/20 shadow-[0_0_25px_rgba(6,182,212,0.15)]">
                            <GitBranch className="text-cyan-400" size={32} />
                        </div>
                        <div>
                            <h3 className="text-xl font-black uppercase tracking-[0.4em] text-cyan-400 leading-none">Knowledge Graph Intelligence</h3>
                            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.3em] mt-3">Deep Relational Mapping Analysis</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-20">
                        {/* Artifacts */}
                        {graphAnalysis.artifacts?.length > 0 && (
                            <div className="space-y-10">
                                <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-rose-400/80 flex items-center gap-3">
                                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.5)]" />
                                    Structural Anomalies
                                </h4>
                                <div className="space-y-8 mt-12">
                                    {graphAnalysis.artifacts.map((art, i) => (
                                        <div key={i} className="p-7 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] transition-all group relative overflow-hidden">
                                            <div className="flex flex-col gap-3">
                                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                                    <span className="text-[11px] font-black text-white uppercase tracking-wider leading-tight">{art.type?.replace(/_/g, " ")}</span>
                                                    <span className="text-[9px] px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/10 font-black shrink-0 w-fit">ARTIFACT</span>
                                                </div>
                                                <p className="text-[13px] text-gray-400 leading-relaxed font-medium break-words">{art.label}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Inferences */}
                        {graphAnalysis.inferences?.length > 0 && (
                            <div className="space-y-10">
                                <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400/80 flex items-center gap-3">
                                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.5)]" />
                                    Derived Conclusions
                                </h4>
                                <div className="space-y-8 mt-12">
                                    {graphAnalysis.inferences.map((inf, i) => (
                                        <div key={i} className="p-7 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] transition-all group relative overflow-hidden">
                                            <div className="flex flex-col gap-3">
                                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                                    <span className="text-[11px] font-black text-white uppercase tracking-wider leading-tight">{inf.type?.replace(/_/g, " ")}</span>
                                                    <span className="text-[9px] px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/10 font-black shrink-0 w-fit">INFERENCE</span>
                                                </div>
                                                <p className="text-[13px] text-gray-400 leading-relaxed font-medium break-words">{inf.label}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* ── LLM Reasoning ── */}
            {llmReasoning.analysis && (
                <div className="card-glass border border-white/10 p-10 relative overflow-visible bg-indigo-500/[0.02] rounded-[2.5rem]">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 blur-[120px] rounded-full -mr-48 -mt-48 pointer-events-none" />
                    
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-10 mb-10 relative">
                        <div className="flex items-center gap-6">
                            <div className="w-14 h-14 rounded-[1.2rem] bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 shadow-[0_0_30px_rgba(99,102,241,0.15)]">
                                <Brain className="text-indigo-400" size={28} />
                            </div>
                            <div>
                                <h3 className="text-base font-black uppercase tracking-[0.2em] text-white">Expert System Reasoning</h3>
                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-1">High-level semantic contextual analysis</p>
                            </div>
                        </div>
                        {llmReasoning.confidence_level && (
                            <div className={`px-5 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-[0.15em] flex items-center gap-3 border shadow-2xl ${
                                llmReasoning.confidence_level === "HIGH" 
                                ? "bg-rose-500/10 text-rose-400 border-rose-500/30 shadow-rose-500/10" 
                                : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-emerald-500/10"
                            }`}>
                                <Zap size={14} className={llmReasoning.confidence_level === "HIGH" ? "animate-pulse" : ""} />
                                {llmReasoning.confidence_level} CONFIDENCE
                            </div>
                        )}
                    </div>

                    <div className="grid grid-cols-1 xl:grid-cols-1 gap-10 text-left items-start relative z-10">
                        {/* Analysis Text - Full Width for Cleanliness */}
                        <div className="p-8 md:p-12 rounded-[2.5rem] bg-black/40 border border-white/5 relative shadow-xl">
                            <p className="text-sm md:text-[15px] leading-relaxed text-gray-300 italic font-medium">
                                {llmReasoning.analysis}
                            </p>
                        </div>

                        {/* Corroborating Signals - Grid Layout for Space */}
                        {llmReasoning.corroborating_signals?.length > 0 && (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {llmReasoning.corroborating_signals.slice(0, 3).map((sig, i) => (
                                    <div key={i} className="flex items-center gap-4 p-5 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.06] transition-all group">
                                        <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center shrink-0 border border-indigo-500/10">
                                            <Zap size={14} className="text-indigo-400" />
                                        </div>
                                        <span className="text-xs font-semibold text-gray-400 leading-snug">{sig}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
