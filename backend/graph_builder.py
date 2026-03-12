# graph_builder.py — Forensic Feature Graph Construction
# Converts structured forensic features into a knowledge graph using NetworkX.
# Optionally persists to Neo4j for GraphRAG retrieval.

import os
import uuid
from datetime import datetime, timezone

import networkx as nx
from neo4j import GraphDatabase

from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────────────────────────────────
# Feature → Artifact Mapping Rules
# Each forensic feature, when above its threshold, implies a forensic
# artifact (a human-interpretable manipulation indicator).
# ─────────────────────────────────────────────────────────────────────

FEATURE_ARTIFACT_MAP: dict[str, dict] = {
    "gan_noise": {
        "threshold": 0.5,
        "artifact": "synthetic_generation",
        "label": "GAN fingerprint pattern detected",
        "edge_label": "indicates",
    },
    "face_blending": {
        "threshold": 0.45,
        "artifact": "face_swap",
        "label": "Face boundary blending artifact",
        "edge_label": "indicates",
    },
    "temporal_jump": {
        "threshold": 0.4,
        "artifact": "frame_manipulation",
        "label": "Temporal frame inconsistency",
        "edge_label": "indicates",
    },
    "lip_sync_error": {
        "threshold": 0.4,
        "artifact": "lip_sync_mismatch",
        "label": "Lip sync does not match facial movement",
        "edge_label": "indicates",
    },
    "eye_blink_anomaly": {
        "threshold": 0.5,
        "artifact": "blink_anomaly",
        "label": "Abnormal eye blink pattern",
        "edge_label": "indicates",
    },
    "lighting_inconsistency": {
        "threshold": 0.45,
        "artifact": "lighting_mismatch",
        "label": "Lighting inconsistency between face and background",
        "edge_label": "indicates",
    },
    "background_coherence": {
        "threshold": 0.4,
        "artifact": "background_warp",
        "label": "Background warping or motion artifact",
        "edge_label": "indicates",
    },
    "spectral_artifact": {
        "threshold": 0.35,
        "artifact": "frequency_anomaly",
        "label": "AI-specific frequency domain artifacts detected",
        "edge_label": "indicates",
    },
    "texture_perfection": {
        "threshold": 0.55,
        "artifact": "skin_texture_anomaly",
        "label": "Unnatural skin texture 'perfection' indicator",
        "edge_label": "indicates",
    },
}

# Artifact → Inference reasoning chains
ARTIFACT_INFERENCE_MAP: dict[str, dict] = {
    "synthetic_generation": {
        "inference": "ai_generated_content",
        "label": "Content is likely AI-generated",
        "edge_label": "supports",
    },
    "face_swap": {
        "inference": "deepfake_manipulation",
        "label": "Face swap manipulation detected",
        "edge_label": "supports",
    },
    "frame_manipulation": {
        "inference": "video_tampering",
        "label": "Video frames have been tampered with",
        "edge_label": "supports",
    },
    "lip_sync_mismatch": {
        "inference": "deepfake_manipulation",
        "label": "Face and audio/lip movement are mismatched",
        "edge_label": "supports",
    },
    "blink_anomaly": {
        "inference": "deepfake_manipulation",
        "label": "Eye blink pattern is not natural",
        "edge_label": "supports",
    },
    "lighting_mismatch": {
        "inference": "composite_media",
        "label": "Media appears composited from multiple sources",
        "edge_label": "supports",
    },
    "background_warp": {
        "inference": "video_tampering",
        "label": "Background shows signs of warping during face manipulation",
        "edge_label": "supports",
    },
    "frequency_anomaly": {
        "inference": "ai_generated_content",
        "label": "Frequency artifacts strongly support AI generation",
        "edge_label": "supports",
    },
    "skin_texture_anomaly": {
        "inference": "ai_generated_content",
        "label": "Overly uniform skin suggests synthetic rendering",
        "edge_label": "supports",
    },
}


# ─────────────────────────────────────────────────────────────────────
# In-Memory Graph Builder (NetworkX)
# ─────────────────────────────────────────────────────────────────────

def build_feature_graph(forensic_payload: dict) -> nx.DiGraph:
    """
    Build a directed knowledge graph from a forensic feature payload.

    Nodes:
        - Media (the analyzed media item)
        - Feature (each forensic feature score)
        - Artifact (inferred manipulation indicators, only for features above threshold)
        - Inference (high-level conclusions)

    Edges:
        - Media → has_feature → Feature
        - Feature → indicates → Artifact
        - Artifact → supports → Inference

    Args:
        forensic_payload: Output from feature_extractor.extract_forensic_features()

    Returns:
        nx.DiGraph with typed nodes and labeled edges.
    """
    G = nx.DiGraph()
    media_id = f"media_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()

    # ── Media node ──
    G.add_node(
        media_id,
        node_type="Media",
        media_type=forensic_payload.get("media_type", "video"),
        model_probability=forensic_payload.get("model_probability", 0.0),
        timestamp=timestamp,
    )

    features = forensic_payload.get("features", {})
    triggered_artifacts = set()

    for feature_name, score in features.items():
        feature_node_id = f"feature_{feature_name}"

        # ── Feature node ──
        G.add_node(
            feature_node_id,
            node_type="Feature",
            feature_name=feature_name,
            score=score,
        )
        G.add_edge(media_id, feature_node_id, relation="has_feature")

        # ── Check if threshold is exceeded → create Artifact node ──
        rule = FEATURE_ARTIFACT_MAP.get(feature_name)
        if rule and score >= rule["threshold"]:
            artifact_id = f"artifact_{rule['artifact']}"

            if artifact_id not in G:
                G.add_node(
                    artifact_id,
                    node_type="Artifact",
                    artifact_type=rule["artifact"],
                    label=rule["label"],
                )
            G.add_edge(
                feature_node_id, artifact_id, relation=rule["edge_label"]
            )
            triggered_artifacts.add(rule["artifact"])

    # ── Inference nodes (only for triggered artifacts) ──
    for artifact_type in triggered_artifacts:
        inf_rule = ARTIFACT_INFERENCE_MAP.get(artifact_type)
        if inf_rule:
            inference_id = f"inference_{inf_rule['inference']}"
            if inference_id not in G:
                G.add_node(
                    inference_id,
                    node_type="Inference",
                    inference_type=inf_rule["inference"],
                    label=inf_rule["label"],
                )
            artifact_id = f"artifact_{artifact_type}"
            G.add_edge(
                artifact_id, inference_id, relation=inf_rule["edge_label"]
            )

    return G


def compute_graph_score(G: nx.DiGraph) -> float:
    """
    Compute a graph-based deepfake confidence score.

    The score is based on the proportion of forensic features that triggered
    artifact nodes, weighted by their individual scores.

    Returns:
        Float between 0.0 and 1.0.
    """
    feature_nodes = [
        n for n, d in G.nodes(data=True) if d.get("node_type") == "Feature"
    ]
    artifact_nodes = [
        n for n, d in G.nodes(data=True) if d.get("node_type") == "Artifact"
    ]

    if not feature_nodes:
        return 0.0

    # Weighted score: sum of scores of features that triggered artifacts
    triggered_features = []
    for feat_node in feature_nodes:
        successors = list(G.successors(feat_node))
        is_triggered = any(
            G.nodes[s].get("node_type") == "Artifact" for s in successors
        )
        if is_triggered:
            triggered_features.append(G.nodes[feat_node].get("score", 0.0))

    if not triggered_features:
        return 0.0

    # Coverage: what fraction of features triggered?
    coverage = len(triggered_features) / len(feature_nodes)
    # Intensity: average score of triggered features
    intensity = float(np.mean(triggered_features)) if triggered_features else 0.0

    # Combine coverage and intensity
    score = 0.6 * intensity + 0.4 * coverage

    return round(min(max(score, 0.0), 1.0), 4)


def graph_to_summary(G: nx.DiGraph) -> dict:
    """
    Extract a human-readable summary from the graph.

    Returns:
        Dict with triggered artifacts, inferences, and a reasons list.
    """
    artifacts = []
    inferences = []
    reasons = []

    for node_id, data in G.nodes(data=True):
        if data.get("node_type") == "Artifact":
            artifacts.append({
                "type": data.get("artifact_type"),
                "label": data.get("label"),
            })
            reasons.append(data.get("label", ""))
        elif data.get("node_type") == "Inference":
            inferences.append({
                "type": data.get("inference_type"),
                "label": data.get("label"),
            })

    return {
        "artifacts": artifacts,
        "inferences": inferences,
        "reasons": reasons,
    }


# ─────────────────────────────────────────────────────────────────────
# Neo4j Persistence (optional — gracefully degrades if unavailable)
# ─────────────────────────────────────────────────────────────────────

# Lazy import to avoid crash at load time if neo4j is not configured
import numpy as np  # needed for compute_graph_score

_neo4j_driver = None


def get_neo4j_driver():
    """Return a cached Neo4j driver, or None if not configured."""
    global _neo4j_driver
    if _neo4j_driver is not None:
        return _neo4j_driver

    uri = os.getenv("NEO4J_URI", "").strip()
    user = os.getenv("NEO4J_USER", "").strip()
    password = os.getenv("NEO4J_PASSWORD", "").strip()

    if not uri or not user or not password:
        return None

    try:
        _neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))
        _neo4j_driver.verify_connectivity()
        print("✅ Neo4j connected")
        return _neo4j_driver
    except Exception as e:
        print(f"⚠️  Neo4j connection failed: {e}")
        _neo4j_driver = None
        return None


def persist_to_neo4j(G: nx.DiGraph) -> bool:
    """
    Write a NetworkX graph to Neo4j. Returns True if successful.
    Gracefully returns False if Neo4j is not available.
    """
    driver = get_neo4j_driver()
    if driver is None:
        return False

    try:
        with driver.session() as session:
            # Create nodes
            for node_id, data in G.nodes(data=True):
                node_type = data.get("node_type", "Unknown")
                props = {k: v for k, v in data.items() if k != "node_type"}
                props["node_id"] = node_id

                session.run(
                    f"MERGE (n:{node_type} {{node_id: $node_id}}) "
                    f"SET n += $props",
                    node_id=node_id,
                    props=props,
                )

            # Create edges
            for src, dst, edge_data in G.edges(data=True):
                relation = edge_data.get("relation", "RELATED_TO").upper()
                src_type = G.nodes[src].get("node_type", "Unknown")
                dst_type = G.nodes[dst].get("node_type", "Unknown")

                session.run(
                    f"MATCH (a:{src_type} {{node_id: $src}}), "
                    f"(b:{dst_type} {{node_id: $dst}}) "
                    f"MERGE (a)-[r:{relation}]->(b)",
                    src=src,
                    dst=dst,
                )

        return True
    except Exception as e:
        print(f"⚠️  Failed to persist graph to Neo4j: {e}")
        return False


def query_related_indicators(feature_name: str) -> list[dict]:
    """
    Query Neo4j for historical correlation between a feature and
    deepfake indicators across past analyses.

    Returns list of related artifact/inference nodes.
    """
    driver = get_neo4j_driver()
    if driver is None:
        return []

    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (f:Feature {feature_name: $feature_name})-[:INDICATES]->(a:Artifact)
                       -[:SUPPORTS]->(i:Inference)
                RETURN a.artifact_type AS artifact, a.label AS artifact_label,
                       i.inference_type AS inference, i.label AS inference_label,
                       f.score AS score
                ORDER BY f.score DESC
                LIMIT 20
                """,
                feature_name=feature_name,
            )
            return [dict(record) for record in result]
    except Exception as e:
        print(f"⚠️  Neo4j query failed: {e}")
        return []
