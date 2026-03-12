import { Activity, Brain, GitBranch, Cpu, Zap } from "lucide-react";

// Human-friendly feature labels and descriptions
const FEATURE_META = {
    gan_noise: { label: "GAN Noise", icon: "🔬", color: "#8b5cf6" },
    face_blending: { label: "Face Blending", icon: "🎭", color: "#ec4899" },
    temporal_jump: { label: "Temporal Jump", icon: "⏱️", color: "#f59e0b" },
    lip_sync_error: { label: "Lip Sync Error", icon: "👄", color: "#ef4444" },
    eye_blink_anomaly: { label: "Eye Blink Anomaly", icon: "👁️", color: "#06b6d4" },
    lighting_inconsistency: { label: "Lighting Inconsistency", icon: "💡", color: "#f97316" },
    background_coherence: { label: "Background Coherence", icon: "🖼️", color: "#10b981" },
    spectral_artifact: { label: "Spectral Artifacts", icon: "📡", color: "#6366f1" },
    texture_perfection: { label: "Texture Perfection", icon: "🧖", color: "#f472b6" },
};

function FeatureBar({ name, score }) {
    const meta = FEATURE_META[name] || { label: name, icon: "📊", color: "#6b7280" };
    const pct = Math.round(score * 100);
    const isHigh = score >= 0.5;

    return (
        <div className="feature-bar-row">
            <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-medium flex items-center gap-2" style={{ color: "var(--color-text-body)" }}>
                    <span className="text-base">{meta.icon}</span>
                    {meta.label}
                </span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${isHigh ? "feature-score-high" : "feature-score-low"}`}>
                    {pct}%
                </span>
            </div>
            <div className="feature-bar-track">
                <div
                    className="feature-bar-fill"
                    style={{
                        width: `${pct}%`,
                        background: isHigh
                            ? `linear-gradient(90deg, ${meta.color}, ${meta.color}dd)`
                            : `linear-gradient(90deg, ${meta.color}44, ${meta.color}88)`,
                    }}
                />
            </div>
        </div>
    );
}

function PipelineScoreCard({ label, score, icon, color }) {
    const pct = Math.round(score * 100);
    return (
        <div className="pipeline-score-card">
            <div className="flex items-center gap-2 mb-2">
                {icon}
                <span className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    {label}
                </span>
            </div>
            <div className="text-2xl font-black" style={{ color }}>{pct}%</div>
            <div className="feature-bar-track mt-2">
                <div className="feature-bar-fill" style={{ width: `${pct}%`, background: color }} />
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
        <div className="mt-6 space-y-5 fade-in">

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
                <div className="card p-7">
                    <h3 className="text-xs font-bold uppercase tracking-wider mb-5 flex items-center gap-2"
                        style={{ color: "var(--color-text-muted)" }}>
                        <Activity size={14} />
                        Forensic Feature Analysis
                    </h3>
                    <div className="space-y-4">
                        {Object.entries(features)
                            .sort(([, a], [, b]) => b - a)
                            .map(([name, score]) => (
                                <FeatureBar key={name} name={name} score={score} />
                            ))}
                    </div>
                </div>
            )}

            {/* ── Graph Analysis (Artifacts + Inferences) ── */}
            {(graphAnalysis.artifacts?.length > 0 || graphAnalysis.inferences?.length > 0) && (
                <div className="card p-7">
                    <h3 className="text-xs font-bold uppercase tracking-wider mb-5 flex items-center gap-2"
                        style={{ color: "var(--color-text-muted)" }}>
                        <GitBranch size={14} />
                        Knowledge Graph Analysis
                    </h3>

                    {graphAnalysis.artifacts?.length > 0 && (
                        <div className="mb-4">
                            <p className="text-xs font-semibold uppercase tracking-wider mb-3"
                                style={{ color: "var(--color-danger)" }}>
                                Detected Artifacts
                            </p>
                            <div className="space-y-2">
                                {graphAnalysis.artifacts.map((art, i) => (
                                    <div key={i} className="flex items-start gap-2.5 text-sm"
                                        style={{ color: "var(--color-text-body)" }}>
                                        <span className="mt-1.5 w-2 h-2 rounded-full shrink-0"
                                            style={{ background: "var(--color-danger)" }} />
                                        <div>
                                            <span className="font-semibold">{art.type?.replace(/_/g, " ")}</span>
                                            {art.label && (
                                                <span className="text-xs ml-2" style={{ color: "var(--color-text-muted)" }}>
                                                    — {art.label}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {graphAnalysis.inferences?.length > 0 && (
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider mb-3"
                                style={{ color: "var(--color-primary)" }}>
                                Inferred Conclusions
                            </p>
                            <div className="space-y-2">
                                {graphAnalysis.inferences.map((inf, i) => (
                                    <div key={i} className="flex items-start gap-2.5 text-sm"
                                        style={{ color: "var(--color-text-body)" }}>
                                        <span className="mt-1.5 w-2 h-2 rounded-full shrink-0"
                                            style={{ background: "var(--color-primary)" }} />
                                        <div>
                                            <span className="font-semibold">{inf.type?.replace(/_/g, " ")}</span>
                                            {inf.label && (
                                                <span className="text-xs ml-2" style={{ color: "var(--color-text-muted)" }}>
                                                    — {inf.label}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* ── LLM Reasoning ── */}
            {llmReasoning.analysis && (
                <div className="card p-7">
                    <h3 className="text-xs font-bold uppercase tracking-wider mb-5 flex items-center gap-2"
                        style={{ color: "var(--color-text-muted)" }}>
                        <Brain size={14} />
                        LLM Expert Reasoning
                    </h3>

                    {llmReasoning.confidence_level && (
                        <div className="mb-4">
                            <span className={`badge ${llmReasoning.confidence_level === "HIGH" ? "badge-fake"
                                    : llmReasoning.confidence_level === "LOW" ? "badge-real"
                                        : "badge-uncertain"
                                }`}>
                                {llmReasoning.confidence_level} Confidence
                            </span>
                        </div>
                    )}

                    <p className="text-sm leading-relaxed mb-4" style={{ color: "var(--color-text-body)" }}>
                        {llmReasoning.analysis}
                    </p>

                    {llmReasoning.corroborating_signals?.length > 0 && (
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider mb-2"
                                style={{ color: "var(--color-text-muted)" }}>
                                Corroborating Signals
                            </p>
                            <ul className="space-y-1.5">
                                {llmReasoning.corroborating_signals.map((sig, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm"
                                        style={{ color: "var(--color-text-light)" }}>
                                        <span className="mt-1 text-xs">🔗</span>
                                        {sig}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
