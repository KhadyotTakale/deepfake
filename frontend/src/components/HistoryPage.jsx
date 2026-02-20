import { useState, useEffect } from "react";
import { RefreshCw, FileText, ImageIcon, Video, ShieldCheck, ShieldAlert, ShieldQuestion, Inbox } from "lucide-react";
import { getHistory } from "../api";

const typeIcons = { news: FileText, image: ImageIcon, video: Video };
const typeLabels = { news: "News", image: "Image", video: "Video" };

export default function HistoryPage() {
    const [detections, setDetections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchHistory = async () => {
        setLoading(true); setError("");
        try {
            const data = await getHistory();
            setDetections(data.detections || []);
        } catch (e) {
            setError(e.message || "Failed to fetch history.");
        } finally { setLoading(false); }
    };

    useEffect(() => { fetchHistory(); }, []);

    return (
        <div className="fade-in">
            {/* Header bar */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <p className="text-sm" style={{ color: "var(--color-text-light)" }}>
                        {detections.length} scan{detections.length !== 1 ? "s" : ""} recorded
                    </p>
                </div>
                <button onClick={fetchHistory} disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50"
                    style={{ background: "var(--color-bg-card)", color: "var(--color-text-light)", border: "1px solid var(--color-border)" }}>
                    <RefreshCw size={14} className={loading ? "spinner" : ""} />
                    Refresh
                </button>
            </div>

            {error && (
                <div className="card p-4 mb-4 text-sm" style={{ background: "var(--color-danger-bg)", color: "var(--color-danger)" }}>{error}</div>
            )}

            {loading && detections.length === 0 ? (
                <div className="card p-12 text-center">
                    <div className="inline-block w-8 h-8 border-3 rounded-full spinner mb-3"
                        style={{ borderColor: "var(--color-primary-lighter)", borderTopColor: "var(--color-primary)" }} />
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>Loading history…</p>
                </div>
            ) : detections.length === 0 ? (
                <div className="card p-12 text-center">
                    <Inbox size={40} style={{ color: "var(--color-text-muted)" }} className="mx-auto mb-3" />
                    <p className="text-base font-semibold mb-1" style={{ color: "var(--color-text-body)" }}>No detections yet</p>
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>Results will appear here after you run an analysis.</p>
                </div>
            ) : (
                <div className="card overflow-hidden">
                    {/* Table header */}
                    <div className="grid gap-6 px-8 py-5 text-xs font-bold uppercase tracking-widest"
                        style={{ gridTemplateColumns: "100px 1fr 100px 80px 160px", color: "var(--color-text-muted)", borderBottom: "1px solid var(--color-border-light)" }}>
                        <span>Type</span>
                        <span>Preview</span>
                        <span>Verdict</span>
                        <span>Score</span>
                        <span>Date</span>
                    </div>

                    {/* Rows */}
                    {detections.map((d, i) => {
                        const TypeIcon = typeIcons[d.type] || FileText;
                        const isReal = d.verdict === "REAL";
                        const isFake = d.verdict === "FAKE";
                        const badgeClass = isReal ? "badge-real" : isFake ? "badge-fake" : "badge-uncertain";

                        return (
                            <div key={d.id || i}
                                className="grid gap-6 px-8 py-5 items-center transition-colors duration-150"
                                style={{
                                    gridTemplateColumns: "100px 1fr 100px 80px 160px",
                                    borderBottom: "1px solid var(--color-border-light)",
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = "var(--color-bg-input)"}
                                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                                {/* Type */}
                                <div className="flex items-center gap-2">
                                    <TypeIcon size={15} style={{ color: "var(--color-primary)" }} />
                                    <span className="text-xs font-semibold capitalize" style={{ color: "var(--color-text-body)" }}>{typeLabels[d.type] || d.type}</span>
                                </div>

                                {/* Preview */}
                                <p className="text-sm truncate" style={{ color: "var(--color-text-light)" }}>
                                    {d.input_preview || d.summary || "—"}
                                </p>

                                {/* Verdict */}
                                <span className={`badge ${badgeClass}`}>{d.verdict}</span>

                                {/* Score */}
                                <span className="text-sm font-semibold" style={{ color: "var(--color-text-heading)" }}>{d.confidence}%</span>

                                {/* Date */}
                                <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                    {d.created_at ? new Date(d.created_at).toLocaleString() : "—"}
                                </span>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
