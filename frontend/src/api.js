const API_BASE = "http://localhost:8000";

export async function detectNews(text) {
    const res = await fetch(`${API_BASE}/detect/news`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
}

export async function detectImage(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/detect/image`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
}

export async function detectVideo(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/detect/video`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
}

/**
 * Call the detailed video detection endpoint.
 * Returns full forensic breakdown: features, graph analysis,
 * pipeline scores, and LLM reasoning.
 */
export async function detectVideoDetailed(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/detect/video/detailed`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
}

export async function getHistory() {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
}
