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
            <div className="flex items-center justify-between mb-10">
                <div>
                    <h2 className="text-2xl font-black text-white tracking-tight mb-2">Scan History</h2>
                    <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">
                        {detections.length} recorded analytical sessions
                    </p>
                </div>
                <button onClick={fetchHistory} disabled={loading}
                    className="flex items-center gap-3 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest cursor-pointer disabled:opacity-50 transition-all border border-white/10 bg-white/5 hover:bg-white/10 text-white">
                    <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
                    Refresh Database
                </button>
            </div>

            {error && (
                <div className="card p-4 mb-4 text-sm" style={{ background: "var(--color-danger-bg)", color: "var(--color-danger)" }}>{error}</div>
            )}

            {loading && detections.length === 0 ? (
                <div className="card-glass border border-white/10 p-24 text-center">
                    <div className="w-12 h-12 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto mb-6" />
                    <p className="text-sm font-bold uppercase tracking-widest text-indigo-400">Loading forensics database…</p>
                </div>
            ) : detections.length === 0 ? (
                <div className="card-glass border border-white/10 p-24 text-center relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-3xl rounded-full" />
                    <Inbox size={48} className="text-gray-500 mx-auto mb-6" />
                    <p className="text-xl font-bold text-white mb-2">Clean Record</p>
                    <p className="text-sm text-gray-500 max-w-xs mx-auto">No detection reports were found in the archive. Your analysis history will appear here.</p>
                </div>
            ) : (
                <div className="card-glass border border-white/10 overflow-hidden shadow-2xl">
                    {/* Table header */}
                    <div className="grid gap-6 px-10 py-6 text-[10px] font-black uppercase tracking-[0.2em] bg-white/5"
                        style={{ gridTemplateColumns: "100px 1fr 120px 80px 160px", color: "var(--color-text-muted)" }}>
                        <span>Source Type</span>
                        <span>Analysis Summary</span>
                        <span>Verdict</span>
                        <span>Confidence</span>
                        <span>Date & Time</span>
                    </div>

                    {/* Rows */}
                    <div className="divide-y divide-white/5">
                        {detections.map((d, i) => {
                            const TypeIcon = typeIcons[d.type] || FileText;
                            const isReal = d.verdict === "REAL";
                            const isFake = d.verdict === "FAKE";
                            const barColor = isReal ? "var(--color-success)" : isFake ? "var(--color-danger)" : "var(--color-warning)";

                            return (
                                <div key={d.id || i}
                                    className="grid gap-6 px-10 py-6 items-center hover:bg-white/[0.02] transition-colors group"
                                    style={{ gridTemplateColumns: "100px 1fr 120px 80px 160px" }}>
                                    {/* Type */}
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-indigo-400 border border-white/5">
                                            <TypeIcon size={14} />
                                        </div>
                                        <span className="text-[10px] font-black uppercase tracking-widest text-gray-500">{d.type}</span>
                                    </div>

                                    {/* Preview */}
                                    <p className="text-sm font-medium text-gray-300 truncate pr-4">
                                        {d.input_preview || d.summary || "No description provided"}
                                    </p>

                                    {/* Verdict */}
                                    <div className="flex">
                                        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm ${
                                            isReal ? "bg-emerald-500/10 text-emerald-500" : isFake ? "bg-rose-500/10 text-rose-500" : "bg-amber-500/10 text-amber-500"
                                        }`}>
                                            {d.verdict}
                                        </span>
                                    </div>

                                    {/* Score */}
                                    <span className="text-sm font-black text-white">{d.confidence}%</span>

                                    {/* Date */}
                                    <div className="text-right sm:text-left">
                                        <span className="text-[11px] font-medium text-gray-600 block">
                                            {d.created_at ? new Date(d.created_at).toLocaleDateString() : d.date || "—"}
                                        </span>
                                        <span className="text-[10px] text-gray-700 font-bold">
                                            {d.created_at ? new Date(d.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ""}
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
