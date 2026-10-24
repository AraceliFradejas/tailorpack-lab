"""Generate the portfolio's SVG figures from saved, validated artifacts."""
import argparse
from html import escape
import json
from pathlib import Path

from .geometry import bounds, side
from .scale import read_packings
from .solvers import grid


def text(x, y, value, size=20, color="#14293d", weight="400", anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'


def gallery(packings):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="960" viewBox="0 0 1200 960" role="img" aria-labelledby="title desc">',
             '<title id="title">tAilorPack: grid and improved square packings</title>',
             '<desc id="desc">Five squares: container side 3 to 2.7071. Ten squares: 4 to 3.9101. Same unit scale within each comparison. Offline validation only.</desc>',
             '<rect width="1200" height="960" fill="#eef3f7"/>',
             text(40, 54, "tAilorPack", 36, weight="700"),
             text(40, 88, "Geometría, búsqueda y verificación reproducible", 21, "#526879")]
    for row, n in enumerate((5, 10)):
        scale = 77 if n == 5 else 58
        for col, (label, squares) in enumerate((("Rejilla de referencia", grid(n)), ("Mejor candidato guardado", packings[n]))):
            x, y = 40+570*col, 120+365*row
            length = side(squares)
            parts += [f'<rect x="{x}" y="{y}" width="550" height="345" rx="16" fill="white"/>',
                      text(x+22,y+35, f"n={n} · {label}", 20, weight="700"),
                      text(x+22,y+64,f"L = {length:.6f}",18,"#526879")]
            dx, dy = x+24, y+87
            x0, y0, _, _ = bounds(squares)
            parts.append(f'<rect x="{dx}" y="{dy}" width="{length*scale}" height="{length*scale}" fill="#f5f8fa" stroke="#14293d" stroke-width="1.8"/>')
            for i, sq in enumerate(squares):
                points = " ".join(f"{dx+(px-x0)*scale:.4f},{dy+(length-(py-y0))*scale:.4f}" for px,py in sq.corners())
                fill = "#176fa1" if col == 0 else "#008574"
                parts.append(f'<polygon points="{points}" fill="{fill}" fill-opacity=".22" stroke="{fill}" stroke-width="1.5"/>')
                parts.append(text(dx+(sq.x-x0)*scale,dy+(length-(sq.y-y0))*scale+5,i,14,anchor="middle"))
            if col:
                improvement = (1-length/side(grid(n)))*100
                parts += [text(x+315,y+160,f"−{improvement:.2f}%",34,"#008574",weight="700"),
                          text(x+315,y+190,"lado del contenedor",16,"#526879"),
                          text(x+315,y+235,"Validado offline",17,weight="700"),
                          text(x+315,y+261,"métrica oficial v17",16,"#526879")]
    parts += [text(40, 885,"Escala unitaria común en cada fila. El giro de los cuadrados es parte de la solución.",18),
              text(40, 918,"Sin envío a Kaggle. No se afirma optimalidad, récord ni posición en el leaderboard.",17,"#526879"),"</svg>\n"]
    return "\n".join(parts)


def performance(profile):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="570" viewBox="0 0 1200 570" role="img" aria-labelledby="title desc">',
             '<title id="title">Spatial geometry speedup against exhaustive checks</title>',
             '<desc id="desc">Median of three repeats on axis-aligned grids. Validation and repair speedups are workload specific.</desc>',
             '<rect width="1200" height="570" fill="#eef3f7"/>',
             text(40,50,"Comprobar menos pares, conservar el resultado",30,weight="700"),
             text(40,84,"Aceleración medida frente al recorrido exhaustivo · rejillas · mediana de 3 repeticiones",18,"#526879"),
             text(840,118,"Validación",17,"#176fa1"),text(1000,118,"Reparación",17,"#008574")]
    for i,row in enumerate(profile["rows"]):
        y=155+i*66
        parts.append(text(40,y+20,f'n={row["n"]}',20,weight="700"))
        for offset,key,color in ((0,"validate_speedup","#176fa1"),(23,"repair_speedup","#008574")):
            value=row[key]
            width=value*8.6
            parts.append(f'<rect x="165" y="{y+offset}" width="{width:.2f}" height="17" rx="3" fill="{color}"/>')
            parts.append(text(175+width,y+offset+15,f"{value:.2f}×",16,color))
    parts += [text(40,520,"La reparación puede ser más lenta en n pequeño. Los tiempos varían con equipo y carga.",18),
              text(40,548,"Es una medición de geometría, no una aceleración equivalente del optimizador completo.",17,"#526879"),"</svg>\n"]
    return "\n".join(parts)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path("."))
    args=p.parse_args(argv)
    root=args.root
    packings=read_packings(root/"examples/m3-best/candidate_NOT_VALIDATED.csv")
    profile=json.loads((root/"examples/scale-m3/profile.json").read_text())
    out=root/"docs/assets"
    out.mkdir(parents=True,exist_ok=True)
    (out/"gallery.svg").write_text(gallery(packings),encoding="utf-8")
    (out/"performance.svg").write_text(performance(profile),encoding="utf-8")
    print("Generated docs/assets/gallery.svg and performance.svg from saved artifacts")


if __name__=="__main__":
    main()
