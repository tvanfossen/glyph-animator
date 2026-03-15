"""Convert between cubic bezier contours and Lottie path format.

Lottie path format:
    {
        "c": true,           # closed path
        "v": [[x,y], ...],   # vertices (on-curve points)
        "i": [[dx,dy], ...], # in-tangents (RELATIVE to vertex)
        "o": [[dx,dy], ...], # out-tangents (RELATIVE to vertex)
    }

For cubic bezier segment (C₀, C₁, C₂, C₃):
    vertex[i]     = C₀ of segment i
    out-tangent[i]= C₁ - C₀  (handle going forward)
    in-tangent[i] = C₂_prev - C₃_prev  (handle from previous segment's end)

CRITICAL: tangents are RELATIVE to their vertex, not absolute coordinates.
"""

from __future__ import annotations

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


def contour_to_lottie_path(contour: list[Seg]) -> dict:
    """Convert cubic bezier contour to Lottie path value dict."""
    vertices: list[list[float]] = []
    in_tangents: list[list[float]] = []
    out_tangents: list[list[float]] = []

    n = len(contour)
    for i in range(n):
        c0, c1, _, _ = contour[i]
        _, _, c2_prev, c3_prev = contour[(i - 1) % n]

        vertices.append([c0[0], c0[1]])
        out_tangents.append([c1[0] - c0[0], c1[1] - c0[1]])
        in_tangents.append([c2_prev[0] - c3_prev[0], c2_prev[1] - c3_prev[1]])

    return {"c": True, "v": vertices, "i": in_tangents, "o": out_tangents}


def lottie_path_to_contour(path: dict) -> list[Seg]:
    """Convert Lottie path value dict back to cubic bezier contour."""
    vertices = path["v"]
    in_tangents = path["i"]
    out_tangents = path["o"]
    n = len(vertices)

    contour: list[Seg] = []
    for i in range(n):
        j = (i + 1) % n
        c0 = (vertices[i][0], vertices[i][1])
        c1 = (c0[0] + out_tangents[i][0], c0[1] + out_tangents[i][1])
        c3 = (vertices[j][0], vertices[j][1])
        c2 = (c3[0] + in_tangents[j][0], c3[1] + in_tangents[j][1])
        contour.append((c0, c1, c2, c3))
    return contour


def offset_contour(contour: list[Seg], ox: float, oy: float, canvas_h: float) -> list[Seg]:
    """Transform contour from font space to canvas space (Y-flip + offset)."""
    return [
        (
            (c0[0] + ox, canvas_h - (c0[1] + oy)),
            (c1[0] + ox, canvas_h - (c1[1] + oy)),
            (c2[0] + ox, canvas_h - (c2[1] + oy)),
            (c3[0] + ox, canvas_h - (c3[1] + oy)),
        )
        for c0, c1, c2, c3 in contour
    ]
