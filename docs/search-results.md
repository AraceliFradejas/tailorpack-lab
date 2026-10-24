# M2 — Primera búsqueda general y resultados

23-10-2026. Se implementó búsqueda por traslación y rotación de cualquier cuadrado,
con dos políticas: greedy y simulated annealing. Una reparación analítica escala
los centros hasta separar todos los pares sobre algún eje SAT. Se conserva siempre
la mejor solución localmente válida; el resultado final se contrasta con la métrica
oficial. No se afirma optimalidad ni mejora sobre récords conocidos.

## Diseño del experimento

Semillas 0..9, dos métodos, mismo presupuesto de propuestas por método y semilla.
El parámetro `evaluations` cuenta propuestas, incluidas reparaciones descartadas;
no iguala segundos ni coste de CPU. El tiempo se registra aparte. Ambos métodos
parten de M0: rejilla salvo la construcción de cinco cuadrados. La temperatura,
escala de movimientos y margen de reparación están fijados en `search.py`.
Los CSV exportan el mejor resultado observado por n entre métodos y semillas.

La prueba inicial (5,6,7,8,10; 2.000 propuestas; 100 búsquedas) no mejoró M0.
Una exploración posterior en 10..13 con temperatura mayor y 10.000 propuestas
encontró mejora en n=10. Por eso se volvió a ejecutar y guardar n=10 con 10 semillas
y dos métodos en la versión final. Esta selección es exploratoria, no una
evaluación sobre puzzles reservados; no permite afirmar que annealing gane en general.

| n=10, 10.000 propuestas/semilla | Greedy | Annealing |
|---|---:|---:|
| Mejor lado | 4 | 3.9100797962141782 |
| Media del mejor lado por semilla | 4 | 3.9839810684215253 |
| Mediana | 4 | 4 |
| Desviación poblacional | 0 | 0.030339098164935883 |
| Semillas con mejora >1e-7 | 0/10 | 3/10 |

Mejor semilla: 4. Reducción del lado frente a rejilla: **2,248 %**.
La mediana sigue en 4: el éxito no es consistente entre semillas.

Una ablation separada parte de la familia de cinco cuadrados con ángulo cero
(lado ≈3). Con 2.000 propuestas, greedy mejora 10/10 semillas, mejor lado
2.7125322544312187; annealing mejora 7/10, mejor lado 2.8368123368432174.
Ninguno supera la construcción explícita de M0 (2.7071067821865475).
Esta ablation demuestra movimiento útil desde una inicialización floja, no una
mejora adicional del mejor resultado n=5.

## Reproducción

Sin dependencias adicionales para la búsqueda:

```sh
python3 -m tailorpack.benchmark --evaluations 2000 --out runs/search-m2
python3 -m tailorpack.benchmark --ns 10 --evaluations 10000 --out runs/search-n10
python3 -m tailorpack.benchmark --ns 5 --initialization axis-five \
  --evaluations 2000 --out runs/search-ablation
```

Cada carpeta incluye configuración, hash de fuentes, resultados por semilla,
distribuciones, tiempos separados y CSV. El informe de la exploración preliminar
10..13 queda en `runs/` local y fuera del ZIP; para repetirla usar
`--ns 10 11 12 13 --evaluations 10000`.

## Validación y mejor candidato

**29 tests correctos**, incluidos los cinco tests opcionales contra el notebook
oficial. Se verificó reparación de solapamientos rotados, rechazo de centros
coincidentes, reproducción por semilla, conservación del incumbente y mejora real
desde un inicio flojo. Se ejecutó además el punto de entrada oficial sobre el CSV
de n=10 y sobre el candidato combinado.

`examples/m2-best/` conserva M0 en n=1..16 y reemplaza n=10 por el mejor CSV de la
búsqueda. `provenance.json` describe la receta y fija el hash del CSV de origen.
El informe oficial vincula el resultado al hash del candidato combinado.

| Universo de puntuación offline n=1..1000 | Score |
|---|---:|
| Rejilla en n=1..16, resto omitido | 28.937669916550586 |
| M0: mejora n=5, resto rejilla/omitido | 28.80668408751468 |
| M2: mejoras n=5 y n=10, resto rejilla/omitido | 28.77824882235171 |

Los 16 puzzles entregados fueron aceptados por el notebook v17 sin modificaciones.
Los puzzles omitidos reciben su penalización. Esto sigue siendo evaluación local
offline: no hay envío ni aceptación en plataforma.

## Estado y siguiente trabajo

M2 tiene implementación, comparación reproducible y una mejora nueva certificada
offline. Queda abierta su meta de rendimiento: mejoras nuevas en varios n,
inicializaciones diversas, movimientos colectivos y checkpoint de búsquedas largas.
La reparación global es barata de implementar pero expande todos los centros al
resolver una colisión: probablemente dificulta reorganizar rejillas densas.
La siguiente prueba debe comparar esa reparación con movimientos de grupos y
diversidad de inicializaciones antes de escalar a n=1000 (M3).
