# Ejecución de referencia

Realizada el 23-10-2026 en el entorno descrito en
`examples/demo/environment.json`.

```sh
python3 -m unittest discover -s tests -v
python3 -m tailorpack --max-n 16 --seed 42 --trials 64 --margin 1e-9 --out examples/demo
```

Resultado: **17 tests correctos**. El test extremo a extremo ejecutó dos veces la
CLI y comparó byte a byte JSON de resultados, CSV y SVG. El test de CSV volvió a
parsear y validar la geometría serializada de n=5. No se ejecutó la matriz remota
de GitHub Actions ni se ejecutó el notebook oficial de Kaggle.

| Magnitud | Valor observado |
|---|---:|
| Puzzles | 1..16 |
| Filas del candidato | 136 |
| Suma exceso rejilla, subconjunto | 2.1667512492977705 |
| Suma exceso experimento, subconjunto | 2.035765420261864 |
| Mejora absoluta del subconjunto | 0.1309858290359065 |
| L para n=5 | 2.7071067821865475 |

Todas las demás soluciones coinciden con la rejilla. No son resultados del
leaderboard ni una certificación de intervalos. La búsqueda no aporta mejora
sobre su propio candidato explícito de 45 grados.
