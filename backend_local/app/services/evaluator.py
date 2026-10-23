import cv2
import numpy as np
import base64
from app.services.cv_preprocessor import base64_to_numpy, numpy_to_base64


def extract_canny_edges(img_bgr: np.ndarray, threshold1=50, threshold2=150) -> np.ndarray:
    """Run Canny edge detection, return binary edge mask"""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1, threshold2)
    # Dilate with 3x3 kernel — gives tolerance for slight spatial offsets
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    return dilated


def calculate_structural_fidelity(sketch_edges: np.ndarray, render_edges: np.ndarray) -> float:
    """
    Structural Fidelity Score — measures how much of the designer's
    sketch intent was preserved and reproduced in the AI render.

    Formula:
        Score = |sketch ∩ render| / |sketch|

    This answers: "What percentage of my sketch edges appeared in the render?"

    Unlike IoU, this is NOT penalised by the render having extra edges
    (textures, furniture, lighting details) — which is expected and desirable.

    Returns float 0.0–1.0. Returns 0.0 if sketch has no edges.
    """
    sketch_bool = sketch_edges > 0
    render_bool  = render_edges  > 0

    sketch_pixel_count = sketch_bool.sum()
    if sketch_pixel_count == 0:
        return 0.0

    # Pixels where both sketch AND render have an edge
    intersection = np.logical_and(sketch_bool, render_bool).sum()

    return float(intersection / sketch_pixel_count)


def calculate_iou(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    """
    Standard Intersection-over-Union between two binary masks.
    Kept for reference. Not used as primary metric.
    IoU = |A ∩ B| / |A ∪ B|
    """
    a_bool = mask_a > 0
    b_bool = mask_b > 0
    intersection = np.logical_and(a_bool, b_bool).sum()
    union        = np.logical_or(a_bool, b_bool).sum()
    if union == 0:
        return 0.0
    return float(intersection / union)


def generate_edge_overlay(sketch_edges: np.ndarray, render_edges: np.ndarray) -> np.ndarray:
    """
    Generate RGB visual overlay composite:
    - Green  : sketch edges reproduced in render  (good match)
    - Red    : sketch edges missing from render   (AI missed your design)
    - Blue   : render edges not in sketch         (AI added detail — expected)
    Returns BGR numpy array (512×512×3)
    """
    a_bool = sketch_edges > 0
    b_bool = render_edges  > 0

    overlap      = np.logical_and(a_bool, b_bool)
    missing      = np.logical_and(a_bool, np.logical_not(b_bool))
    hallucinated = np.logical_and(b_bool, np.logical_not(a_bool))

    h, w = sketch_edges.shape
    overlay = np.zeros((h, w, 3), dtype=np.uint8)
    overlay[overlap]      = [0,   255, 0]    # Green — preserved
    overlay[missing]      = [0,   0,   255]  # Red   — missed
    overlay[hallucinated] = [255, 0,   0]    # Blue  — added by AI

    return overlay


def evaluate_generation(cleaned_sketch_b64: str, rendered_image_b64: str) -> dict:
    """
    Full evaluation pipeline:
    1. Decode both base64 images
    2. Resize both to 512×512 BGR
    3. Extract Canny edges with dilation
    4. Calculate Structural Fidelity Score (primary metric)
    5. Calculate standard IoU (secondary reference)
    6. Generate colour-coded edge overlay
    Returns dict with scores and overlay image
    """
    # 1. Decode
    sketch_bgr = base64_to_numpy(cleaned_sketch_b64)
    render_bgr = base64_to_numpy(rendered_image_b64)

    # 2. Resize to 512×512
    sketch_bgr = cv2.resize(sketch_bgr, (512, 512), interpolation=cv2.INTER_AREA)
    render_bgr = cv2.resize(render_bgr, (512, 512), interpolation=cv2.INTER_AREA)

    # 3. Extract edges
    sketch_edges = extract_canny_edges(sketch_bgr)
    render_edges = extract_canny_edges(render_bgr)

    # 4. Structural Fidelity (primary — shown in UI as %)
    fidelity_score = calculate_structural_fidelity(sketch_edges, render_edges)

    # 5. Standard IoU (secondary reference only)
    iou_score = calculate_iou(sketch_edges, render_edges)

    # 6. Overlay
    overlay_bgr = generate_edge_overlay(sketch_edges, render_edges)
    overlay_b64 = numpy_to_base64(overlay_bgr)

    return {
        # Primary metric — Structural Fidelity stored as edge_similarity_score
        "iou_score":          fidelity_score,
        "edge_overlay_b64":   overlay_b64,
        "sketch_edge_count":  int(np.sum(sketch_edges > 0)),
        "render_edge_count":  int(np.sum(render_edges > 0)),
        # Secondary reference
        "raw_iou":            round(iou_score, 4),
    }
