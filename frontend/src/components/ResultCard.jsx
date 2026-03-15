import { ShieldCheck, ShieldAlert, ShieldQuestion, AlertTriangle, Info } from "lucide-react";
import CircularProgress from "./CircularProgress";

export default function ResultCard({ result, loading, duration }) {
    if (loading) {
        return (
            <div className="mt-6 fade-in">
                <div className="card p-8 text-center">
                    <div className="inline-block w-8 h-8 border-3 rounded-full spinner mb-3"
                        style={{ borderColor: "var(--color-primary-lighter)", borderTopColor: "var(--color-primary)" }} />
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        Analyzing content… {duration > 0 && `(Elapsed: ${Math.floor(duration / 60)}:${(duration % 60).toString().padStart(2, '0')})`}
                    </p>
                </div>
            </div>
        );
    }

    if (!result) return null;

    const isReal = result.verdict === "REAL";
    const isFake = result.verdict === "FAKE";
    const badgeClass = isReal ? "badge-real" : isFake ? "badge-fake" : "badge-uncertain";
    const barColor = isReal ? "var(--color-success)" : isFake ? "var(--color-danger)" : "var(--color-warning)";
    const VerdictIcon = isReal ? ShieldCheck : isFake ? ShieldAlert : ShieldQuestion;

    return (
        <div className="fade-in">
            <div className="card overflow-hidden border border-white/5 bg-gray-900/50 backdrop-blur-xl mx-4 sm:mx-0">
                {/* Header & Percentage */}
                <div className="p-10 flex flex-col md:flex-row items-center justify-between gap-10" style={{ borderBottom: "1px solid var(--color-border-light)" }}>
                    <div className="flex items-center gap-5">
                        <div className="p-4 rounded-2xl" style={{ background: `${barColor}15` }}>
                            <VerdictIcon size={32} style={{ color: barColor }} />
                        </div>
                        <div>
                            <p className="text-xs font-bold uppercase tracking-[0.2em]" style={{ color: "var(--color-text-muted)" }}>Forensic Verdict</p>
                            <div className="flex items-center gap-3 mt-1">
                                <span className={`text-4xl font-black tracking-tighter ${result.verdict === 'FAKE' ? 'text-rose-500' : 'text-emerald-500'}`}>
                                    {result.verdict}
                                </span>
                                <span className={`badge ${badgeClass} h-6`}>{result.confidence}% Match</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-10">
                        <div className="hidden sm:block text-right">
                            <p className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: "var(--color-text-muted)" }}>Process Time</p>
                            <p className="text-xl font-mono font-bold text-white">{Math.floor(duration / 60)}:{(duration % 60).toString().padStart(2, '0')}</p>
                        </div>
                        <CircularProgress percentage={result.confidence} color={barColor} size={100} />
                    </div>
                </div>

                <div className="space-y-16 py-10">
                    {/* Summary Section */}
                    <div className="px-8">
                        <div className="flex items-center gap-2 mb-4">
                            <Info size={16} className="text-indigo-400" />
                            <h4 className="text-xs font-bold uppercase tracking-widest" style={{ color: "var(--color-text-muted)" }}>Executive Summary</h4>
                        </div>
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/5 relative overflow-hidden">
                            <p className="text-[12px] leading-relaxed font-medium text-gray-400 indent-4 italic">
                                "{result.summary}"
                            </p>
                        </div>
                    </div>

                    {/* Reasons */}
                    {result.reasons?.length > 0 && (
                        <div className="px-8">
                            <h4 className="text-sm font-black uppercase tracking-[0.2em] mb-4 text-white">Detailed Forensic Findings</h4>
                            <div className="space-y-3">
                                {result.reasons.slice(0, 4).map((reason, i) => (
                                    <div key={i} className="flex items-start gap-4 p-4 rounded-2xl bg-white/[0.03] border border-white/5 text-gray-200">
                                        <span className="mt-1.5 w-2 h-2 rounded-full shrink-0 shadow-[0_0_8px_var(--color-primary)]" style={{ background: barColor }} />
                                        <span className="text-base font-medium leading-relaxed">{reason}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Disclaimer */}
                    <div className="px-8">
                        <div className="flex items-start gap-3 rounded-xl p-4 text-xs leading-relaxed"
                            style={{ background: "var(--color-warning-bg)", color: "var(--color-warning)" }}>
                            <AlertTriangle size={15} className="mt-0.5 shrink-0" />
                            <span>No detection system is 100% accurate. Verify results independently for critical decisions.</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
