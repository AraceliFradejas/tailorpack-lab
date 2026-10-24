"""Dependency-free SVG for inspecting the experiment."""
from .geometry import bounds, side


def svg(squares):
    x0, y0, _, _ = bounds(squares)
    length = side(squares)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.15 -0.15 {length+.3} {length+.3}">',
             f'<rect x="0" y="0" width="{length}" height="{length}" fill="#f5f7fb" stroke="#172554" stroke-width=".012"/>']
    for i, sq in enumerate(squares):
        points = " ".join(f"{x-x0:.12f},{length-(y-y0):.12f}" for x, y in sq.corners())
        color = "#f59e0b" if i == 4 else "#2563eb"
        parts.append(f'<polygon points="{points}" fill="{color}" fill-opacity=".75" stroke="#172554" stroke-width=".012"/>')
    return "\n".join(parts + ["</svg>\n"])
