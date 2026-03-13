import { ShieldCheck, ShieldAlert, ShieldQuestion, AlertTriangle } from "lucide-react";

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
        <div className="mt-6 fade-in">
            <div className="card overflow-hidden">
                {/* Header */}
                <div className="p-7 flex items-center justify-between" style={{ borderBottom: "1px solid var(--color-border-light)" }}>
                    <div className="flex items-center gap-3">
                        <VerdictIcon size={24} style={{ color: barColor }} />
                        <div>
                            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Analysis Result</p>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className={`badge ${badgeClass}`}>{result.verdict}</span>
                            </div>
                        </div>
                    </div>
                    <div className="text-right flex items-center gap-10">
                        <div className="text-right">
                            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Analysis Time</p>
                            <p className="text-md font-bold mt-0.5" style={{ color: "var(--color-text-heading)" }}>{Math.floor(duration / 60)}:{(duration % 60).toString().padStart(2, '0')}</p>
                        </div>
                        <div className="text-right">
                            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Confidence</p>
                            <p className="text-2xl font-bold mt-0.5" style={{ color: "var(--color-text-heading)" }}>{result.confidence}%</p>
                        </div>
                    </div>
                </div>

                {/* Confidence bar */}
                <div className="px-7 pt-6">
                    <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: "var(--color-border-light)" }}>
                        <div className="h-full rounded-full confidence-bar-fill" style={{ width: `${result.confidence}%`, background: barColor }} />
                    </div>
                </div>

                {/* Summary */}
                <div className="px-7 pt-6 pb-4">
                    <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>Summary</h4>
                    <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-body)" }}>{result.summary}</p>
                </div>

                {/* Reasons */}
                {result.reasons?.length > 0 && (
                    <div className="px-7 pb-6 pt-2">
                        <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--color-text-muted)" }}>Key Findings</h4>
                        <ul className="space-y-2">
                            {result.reasons.map((reason, i) => (
                                <li key={i} className="flex items-start gap-2.5 text-sm" style={{ color: "var(--color-text-body)" }}>
                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0" style={{ background: barColor }} />
                                    {reason}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Disclaimer */}
                <div className="px-7 pb-7 pt-2">
                    <div className="flex items-start gap-3 rounded-xl p-4 text-xs leading-relaxed"
                        style={{ background: "var(--color-warning-bg)", color: "var(--color-warning)" }}>
                        <AlertTriangle size={15} className="mt-0.5 shrink-0" />
                        <span>No detection system is 100% accurate. Verify results independently for critical decisions.</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
