import React from "react";

export default function LandingPage({
  onStartScanning
}) {
  return (
    <div className="bg-[#f6f6f8] text-slate-900 antialiased min-h-screen">

{/* Top Navigation */}
<header className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/80 backdrop-blur-md">
<div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
<div className="flex items-center gap-2">
<div className="flex h-8 w-8 items-center justify-center rounded-lg bg-landing-primary text-white">
<span className="material-symbols-outlined text-xl">fingerprint</span>
</div>
<h2 className="text-xl font-extrabold tracking-tight text-slate-900">DeepTrace<span className="text-landing-primary">AI</span></h2>
</div>
<nav className="hidden md:flex items-center gap-10">
<a className="text-sm font-semibold text-slate-600 hover:text-landing-primary transition-colors" href="#">Forensics</a>
<a className="text-sm font-semibold text-slate-600 hover:text-landing-primary transition-colors" href="#">API Access</a>
<a className="text-sm font-semibold text-slate-600 hover:text-landing-primary transition-colors" href="#">Enterprise</a>
<a className="text-sm font-semibold text-slate-600 hover:text-landing-primary transition-colors" href="#">Research</a>
</nav>
<div className="flex items-center gap-3">
<button className="hidden sm:block px-4 py-2 text-sm font-bold text-slate-700 hover:text-landing-primary transition-colors">Log In</button>
<button className="rounded-full bg-landing-primary px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-landing-primary/20 hover:bg-landing-primary/90 transition-all active:scale-95" onClick={onStartScanning}>
                    Start Scanning
                </button>
</div>
</div>
</header>
<main>
{/* Hero Section */}
<section className="relative overflow-hidden px-6 pt-16 pb-24 md:pt-28 md:pb-32">
<div className="mx-auto max-w-7xl">
<div className="grid items-center gap-12 lg:grid-cols-2">
<div className="flex flex-col gap-8">
<div className="inline-flex items-center gap-2 w-fit rounded-full border border-landing-primary/20 bg-landing-primary/5 px-3 py-1 text-xs font-bold uppercase tracking-wider text-landing-primary">
<span className="relative flex h-2 w-2">
<span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-landing-primary opacity-75"></span>
<span className="relative inline-flex h-2 w-2 rounded-full bg-landing-primary"></span>
</span>
                            v4.0 Live: Real-time Generative Detection
                        </div>
<h1 className="text-5xl font-black leading-[1.1] tracking-tight text-slate-900 md:text-7xl">
                            Unmask the Truth with <span className="text-transparent bg-clip-text bg-gradient-to-r from-landing-primary to-landing-accent-cyan">AI Forensics</span>
</h1>
<p className="max-w-xl text-lg leading-relaxed text-slate-600">
                            Protect your integrity against digital deception. Our industry-leading neural engine identifies manipulated media with 99.8% precision, verified by global intelligence standards.
                        </p>
<div className="flex flex-wrap gap-4">
<button className="flex items-center gap-2 rounded-xl bg-landing-primary px-8 py-4 text-base font-bold text-white shadow-xl shadow-landing-primary/25 hover:shadow-landing-primary/40 transition-all" onClick={onStartScanning}>
                                Analyze Now
                                <span className="material-symbols-outlined">arrow_forward</span>
</button>
<button className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-8 py-4 text-base font-bold text-slate-900 hover:bg-slate-50 transition-all">
                                Request Enterprise Demo
                            </button>
</div>
<div className="flex items-center gap-4 text-sm font-medium text-slate-400">
<span className="flex items-center gap-1"><span className="material-symbols-outlined text-green-500 text-lg">check_circle</span> NIST Certified</span>
<span className="flex items-center gap-1"><span className="material-symbols-outlined text-green-500 text-lg">check_circle</span> SOC2 Type II</span>
<span className="flex items-center gap-1"><span className="material-symbols-outlined text-green-500 text-lg">check_circle</span> Privacy First</span>
</div>
</div>
<div className="relative">
<div className="relative z-10 overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 soft-shadow">
<div className="aspect-video w-full bg-slate-100 rounded-xl bg-cover bg-center overflow-hidden" data-alt="Abstract neural network visualization showing data points and connectivity" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDY2oGElVxWuxDb5nJhl43qiXX9bcn8BwQCDcIcy3VDylEH6W7fHwH4W9wiY8rjo0eWazYRXEwxz5qZtBHfQ6TMdB5bo8EwHgRXsuPPF9lHCx06H9ePoJf0VCaRCaYNUMiViKLF9VEK8j7ANBM-TptG6r1SuXMlGQZBBDfkNniMST3ADNbtfip41Hv0D4MIcWQHeXgru8Lsd09LV7XrzryysHsX_pgUJtddHwfuJ4yAhps9cMIpwLu9vNll9_rvcUDK8bJSnsTkUt8')" }}>
<div className="absolute inset-0 bg-gradient-to-t from-slate-900/40 to-transparent flex items-end p-6">
<div className="flex w-full items-center justify-between rounded-lg bg-white/10 p-3 backdrop-blur-md border border-white/20">
<div className="flex items-center gap-3">
<div className="h-10 w-10 rounded-full bg-landing-primary/20 flex items-center justify-center">
<span className="material-symbols-outlined text-white">scan</span>
</div>
<div className="text-white">
<div className="text-[10px] font-bold uppercase opacity-70">Current Scan</div>
<div className="text-sm font-semibold">Source_Verification_720p.mp4</div>
</div>
</div>
<div className="text-right">
<div className="text-[10px] font-bold uppercase opacity-70 text-white">Confidence</div>
<div className="text-sm font-bold text-landing-accent-cyan tracking-widest">99.82%</div>
</div>
</div>
</div>
</div>
</div>
{/* Decorative background elements */}
<div className="absolute -right-8 -top-8 -z-0 h-64 w-64 rounded-full bg-landing-primary/5 blur-3xl"></div>
<div className="absolute -left-8 -bottom-8 -z-0 h-64 w-64 rounded-full bg-landing-accent-cyan/10 blur-3xl"></div>
</div>
</div>
</div>
</section>
{/* Trust Signals / Logos */}
<section className="border-y border-slate-100 bg-white py-12">
<div className="mx-auto max-w-7xl px-6">
<p className="mb-8 text-center text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Trusted by Global Media and Governments</p>
<div className="flex flex-wrap items-center justify-center gap-12 grayscale opacity-40">
<span className="text-2xl font-black">REUTERS</span>
<span className="text-2xl font-black">BBC</span>
<span className="text-2xl font-black">CNN</span>
<span className="text-2xl font-black">ALJAZEERA</span>
<span className="text-2xl font-black">THE NY TIMES</span>
</div>
</div>
</section>
{/* How It Works / Multi-Modal Section */}
<section className="bg-slate-50 py-24 px-6">
<div className="mx-auto max-w-7xl">
<div className="mb-16 flex flex-col items-center text-center">
<h2 className="mb-4 text-sm font-bold uppercase tracking-widest text-landing-primary">Core Capabilities</h2>
<h3 className="max-w-2xl text-4xl font-black tracking-tight text-slate-900 md:text-5xl">
                        Multi-Modal Verification for the Synthetics Era
                    </h3>
<p className="mt-6 max-w-xl text-lg text-slate-600">
                        Our engine doesn't just look for glitches. It analyzes physiological signals, metadata forensics, and generative artifacts across all digital mediums.
                    </p>
</div>
<div className="grid gap-6 md:grid-cols-3">
{/* Video Analysis */}
<div className="group relative flex flex-col gap-6 rounded-2xl border border-slate-200 bg-white p-8 transition-all hover:border-landing-primary/20 hover:shadow-xl hover:shadow-landing-primary/5">
<div className="inline-flex h-14 w-14 items-center justify-center rounded-xl bg-slate-50 text-landing-primary transition-colors group-hover:bg-landing-primary group-hover:text-white">
<span className="material-symbols-outlined text-3xl">videocam</span>
</div>
<div>
<h4 className="mb-3 text-xl font-bold text-slate-900">Video Analysis</h4>
<p className="text-slate-600 leading-relaxed">
                                Frame-by-frame physiological signal detection, blink rate analysis, and facial inconsistency mapping powered by temporal consistency checks.
                            </p>
</div>
<ul className="mt-2 space-y-2 text-sm font-medium text-slate-500">
<li className="flex items-center gap-2"><span className="material-symbols-outlined text-landing-primary text-base">task_alt</span> Heartbeat (rPPG) detection</li>
<li className="flex items-center gap-2"><span className="material-symbols-outlined text-landing-primary text-base">task_alt</span> Lip-sync verification</li>
</ul>
</div>
{/* Image Forensics */}
<div className="group relative flex flex-col gap-6 rounded-2xl border border-slate-200 bg-white p-8 transition-all hover:border-landing-primary/20 hover:shadow-xl hover:shadow-landing-primary/5">
<div className="inline-flex h-14 w-14 items-center justify-center rounded-xl bg-slate-50 text-landing-primary transition-colors group-hover:bg-landing-primary group-hover:text-white">
<span className="material-symbols-outlined text-3xl">image</span>
</div>
<div>
<h4 className="mb-3 text-xl font-bold text-slate-900">Image Forensics</h4>
<p className="text-slate-600 leading-relaxed">
                                Pixel-level metadata auditing and GAN-generated artifact identification. We detect Diffusion and Transformer based generation traces.
                            </p>
</div>
<ul className="mt-2 space-y-2 text-sm font-medium text-slate-500">
<li className="flex items-center gap-2"><span className="material-symbols-outlined text-landing-primary text-base">task_alt</span> Error Level Analysis (ELA)</li>
<li className="flex items-center gap-2"><span className="material-symbols-outlined text-landing-primary text-base">task_alt</span> Noise profile matching</li>
</ul>
</div>
{/* Audio Authentication */}
<div className="group relative flex flex-col gap-6 rounded-2xl border border-slate-200 bg-white p-8 transition-all hover:border-landing-primary/20 hover:shadow-xl hover:shadow-landing-primary/5">
<div className="inline-flex h-14 w-14 items-center justify-center rounded-xl bg-slate-50 text-landing-primary transition-colors group-hover:bg-landing-primary group-hover:text-white">
<span className="material-symbols-outlined text-3xl">mic</span>
</div>
<div>
<h4 className="mb-3 text-xl font-bold text-slate-900">Audio Authentication</h4>
<p className="text-slate-600 leading-relaxed">
                                Spectrogram analysis to uncover synthetic voice cloning and frequency anomalies. Detects sophisticated text-to-speech models.
                            </p>
</div>
<ul className="mt-2 space-y-2 text-sm font-medium text-slate-500">
<li className="flex items-center gap-2"><span className="material-symbols-outlined text-landing-primary text-base">task_alt</span> Phonetical anomaly detection</li>
<li className="flex items-center gap-2"><span className="material-symbols-outlined text-landing-primary text-base">task_alt</span> Synthetic silence signatures</li>
</ul>
</div>
</div>
</div>
</section>
{/* Stats / Trust Metrics */}
<section className="py-24 px-6 bg-white">
<div className="mx-auto max-w-7xl">
<div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
<div className="rounded-2xl border border-slate-100 bg-slate-50/50 p-8 text-center">
<div className="text-4xl font-black text-landing-primary mb-2">99.8%</div>
<div className="text-sm font-bold uppercase tracking-widest text-slate-500">Detection Accuracy</div>
</div>
<div className="rounded-2xl border border-slate-100 bg-slate-50/50 p-8 text-center">
<div className="text-4xl font-black text-landing-primary mb-2">&lt; 2.4s</div>
<div className="text-sm font-bold uppercase tracking-widest text-slate-500">Analysis Speed</div>
</div>
<div className="rounded-2xl border border-slate-100 bg-slate-50/50 p-8 text-center">
<div className="text-4xl font-black text-landing-primary mb-2">1.2M+</div>
<div className="text-sm font-bold uppercase tracking-widest text-slate-500">Daily Scans</div>
</div>
<div className="rounded-2xl border border-slate-100 bg-slate-50/50 p-8 text-center">
<div className="text-4xl font-black text-landing-primary mb-2">24/7</div>
<div className="text-sm font-bold uppercase tracking-widest text-slate-500">Monitoring</div>
</div>
</div>
</div>
</section>
{/* CTA Section */}
<section className="py-24 px-6">
<div className="mx-auto max-w-7xl rounded-[2rem] bg-slate-900 p-12 md:p-20 relative overflow-hidden">
{/* Background visual */}
<div className="absolute inset-0 opacity-10" style={{ backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)", backgroundSize: "40px 40px" }}></div>
<div className="relative z-10 flex flex-col items-center text-center">
<h2 className="max-w-3xl text-4xl font-black leading-tight text-white md:text-6xl">
                        Verify your content before it's too late.
                    </h2>
<p className="mt-8 max-w-xl text-lg text-slate-400">
                        Join over 5,000 organizations using DeepTrace to secure their digital communication channels and verify news sources.
                    </p>
<div className="mt-12 flex flex-wrap justify-center gap-4">
<button className="rounded-xl bg-landing-primary px-10 py-5 text-lg font-bold text-white hover:bg-landing-primary/90 transition-all" onClick={onStartScanning}>
                            Get Started Free
                        </button>
<button className="rounded-xl border border-white/20 bg-white/5 px-10 py-5 text-lg font-bold text-white backdrop-blur-sm hover:bg-white/10 transition-all">
                            Speak to an Expert
                        </button>
</div>
</div>
</div>
</section>
</main>
<footer className="bg-slate-50 pt-20 pb-10 border-t border-slate-200 px-6">
<div className="mx-auto max-w-7xl">
<div className="grid gap-12 lg:grid-cols-4 md:grid-cols-2">
<div className="flex flex-col gap-6">
<div className="flex items-center gap-2">
<div className="flex h-8 w-8 items-center justify-center rounded-lg bg-landing-primary text-white">
<span className="material-symbols-outlined text-xl">fingerprint</span>
</div>
<h2 className="text-xl font-extrabold tracking-tight text-slate-900">DeepTrace<span className="text-landing-primary">AI</span></h2>
</div>
<p className="text-sm leading-relaxed text-slate-500">
                        The definitive platform for media authentication and deepfake forensics. Protecting truth in the age of generative AI.
                    </p>
<div className="flex gap-4">
<a className="h-10 w-10 flex items-center justify-center rounded-full border border-slate-200 text-slate-400 hover:border-landing-primary hover:text-landing-primary transition-all" href="#">
<span className="material-symbols-outlined text-xl font-icon">share</span>
</a>
<a className="h-10 w-10 flex items-center justify-center rounded-full border border-slate-200 text-slate-400 hover:border-landing-primary hover:text-landing-primary transition-all" href="#">
<span className="material-symbols-outlined text-xl font-icon">public</span>
</a>
</div>
</div>
<div>
<h5 className="mb-6 text-sm font-bold uppercase tracking-widest text-slate-900">Platform</h5>
<ul className="space-y-4 text-sm font-medium text-slate-500">
<li><a className="hover:text-landing-primary transition-colors" href="#">Video Detection</a></li>
<li><a className="hover:text-landing-primary transition-colors" href="#">Audio Forensics</a></li>
<li><a className="hover:text-landing-primary transition-colors" href="#">API Documentation</a></li>
<li><a className="hover:text-landing-primary transition-colors" href="#">Browser Extension</a></li>
</ul>
</div>
<div>
<h5 className="mb-6 text-sm font-bold uppercase tracking-widest text-slate-900">Resources</h5>
<ul className="space-y-4 text-sm font-medium text-slate-500">
<li><a className="hover:text-landing-primary transition-colors" href="#">Case Studies</a></li>
<li><a className="hover:text-landing-primary transition-colors" href="#">Research Papers</a></li>
<li><a className="hover:text-landing-primary transition-colors" href="#">Media Kit</a></li>
<li><a className="hover:text-landing-primary transition-colors" href="#">Ethical AI Charter</a></li>
</ul>
</div>
<div>
<h5 className="mb-6 text-sm font-bold uppercase tracking-widest text-slate-900">Subscribe</h5>
<p className="mb-4 text-sm text-slate-500">Get the latest insights on synthetic media trends.</p>
<div className="flex flex-col gap-2">
<input className="rounded-lg border-slate-200 bg-white px-4 py-2 text-sm focus:border-landing-primary focus:ring-landing-primary" placeholder="Email address" type="email"/>
<button className="rounded-lg bg-slate-900 py-2 text-sm font-bold text-white hover:bg-slate-800 transition-all">Subscribe</button>
</div>
</div>
</div>
<div className="mt-20 border-t border-slate-200 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
<p className="text-xs font-medium text-slate-400">© 2024 DeepTrace AI Technologies Inc. All rights reserved.</p>
<div className="flex gap-6 text-xs font-medium text-slate-400">
<a className="hover:text-slate-900" href="#">Privacy Policy</a>
<a className="hover:text-slate-900" href="#">Terms of Service</a>
<a className="hover:text-slate-900" href="#">Cookie Settings</a>
</div>
</div>
</div>
</footer>

    </div>
  );
}
