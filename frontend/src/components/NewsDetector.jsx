import { useState } from "react";
import { Send } from "lucide-react";
import { detectNews } from "../api";
import ResultCard from "./ResultCard";

export default function NewsDetector() {
    const [text, setText] = useState("");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleAnalyze = async () => {
        if (!text.trim()) { setError("Please enter some text to analyze."); return; }
        setError(""); setResult(null); setLoading(true);
        try {
            const data = await detectNews(text);
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
                        <label className="text-base font-bold mb-6 block" style={{ color: "var(--color-text-heading)" }}>
                            Article / Text Content to Analyze
                        </label>
                        <textarea
                            className="w-full min-h-[260px] rounded-xl p-5 text-base resize-y outline-none leading-relaxed transition-all focus:ring-2 focus:ring-purple-400"
                            style={{ background: "var(--color-bg-input)", color: "var(--color-text-body)", border: "1px solid var(--color-border)" }}
                            placeholder="Paste the news article, social media post, or claim here..."
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                        />
                        <div className="flex flex-col sm:flex-row items-center justify-between mt-5 gap-4">
                            <span className="text-sm font-medium" style={{ color: "var(--color-text-muted)" }}>{text.length} characters</span>
                            <button onClick={handleAnalyze} disabled={loading} className="btn-primary w-full sm:w-auto justify-center">
                                <Send size={16} />
                                {loading ? "Analyzing..." : "Analyze Text"}
                            </button>
                        </div>
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
                            Our AI evaluates text for misinformation, fake news, and propaganda. It's designed to help journalists, researchers, and readers verify claims.
                        </p>
                    </div>

                    <div className="card p-8 md:p-10">
                        <h3 className="text-sm font-bold mb-6 uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>What We Check</h3>
                        <ul className="space-y-3 text-sm font-medium" style={{ color: "var(--color-text-body)" }}>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Sensationalist Language</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Source Credibility</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Logical Inconsistencies</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Clickbait Patterns</li>
                            <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Extreme Bias</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
