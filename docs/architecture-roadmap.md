# Arquitectura y evolución

## Alcance de portfolio

Mostrar formulación matemática, geometría comprobable, diseño de experimentos,
reproducibilidad y comunicación honesta de resultados. La versión 0.1 entrega una
base ejecutable; el proyecto competitivo completo queda dividido en hitos medibles.

Flujo actual: CLI → solver → validación geométrica → métricas locales → JSON/CSV/SVG.
`geometry.py` no depende del solver; `export.py` valida antes de escribir y nunca
llama a Kaggle; no hay acceso de red en la ejecución. `Square` representa centros
y ángulos, sin confundirlos con vértices ni esquinas inferiores.

| Componente | Implementado | Próxima extensión |
|---|---|---|
| Dominio/geometría | Cuadrados, SAT, índice espacial y referencia exhaustiva | Más casos degenerados y otros índices |
| Solvers | Rejilla, familia n=5, greedy y annealing | Movimientos colectivos e inicializaciones diversas |
| Evaluación | Métrica local y adaptador oficial v17 con hash | Revisar cambios futuros de Kaggle |
| Artefactos | CSV, JSON, SVG, checkpoints y catálogo por n | Campañas de mayor presupuesto |
| Calidad | 37 tests, CI definida y comprobador de entrega | Ejecutar CI en el futuro repositorio |
| Presentación | README, galería, caso de estudio, ablations y guion | Elegir licencia, publicar y grabar si se desea |

Decisiones: biblioteca estándar para ejecutar sin instalaciones; presupuesto por
número de muestras, no por reloj; orden estable y RNG privado; entorno separado
del resultado para poder comparar artefactos deterministas. La comprobación SAT
conserva peor caso O(n²); M3 mide casos representativos hasta n=1000.
El margen de separación 1e-9 es una elección local, no tolerancia oficial.
Actualización M3: el filtro espacial evita recorrer todos los pares en casos
dispersos; conserva coste cuadrático en el peor caso. Ver `scaling.md`.

## Estado de las fases

1. **M0 — Base reproducible (entregado).** Ejecutar tests y demo en n=1..16;
   conservar rejilla, construcción, resultado y visual. Aceptación: sin colisiones
   locales, mejora n=5, artefactos repetibles y límites documentados.
2. **M1 — Contrato oficial (completado el 23-10-2026).** Se fijaron sample y
   evaluador v17 con hashes y dependencias; se evaluaron rejilla y candidato n=1..16
   offline, con 23 tests correctos. Evidencia en `official-validation.md`.
   Criterio original: tras acceso autorizado, fijar sample y
   evaluador completo, registrar hashes/licencias/dependencias, pruebas de ida y
   vuelta sobre CSV. Aceptación: grid y n=5 evaluados oficialmente offline;
   diferencias explicadas y errores cubiertos. Solo entonces llamar «validado
   con evaluador oficial» a un archivo; aceptación en plataforma es otro estado.
3. **M2 — Búsqueda general (en curso).** Ya hay movimientos generales,
   greedy/annealing, 10 semillas, budgets iguales, 29 tests y mejora n=10
   validada offline. Ver `search-results.md`. Queda pendiente rendimiento en
   varios puzzles nuevos y diversidad de inicializaciones. Plan: inicializaciones variadas, traslaciones,
   rotaciones, función suave de penalización y reparación factible; comparar
   annealing y búsqueda local con igual presupuesto de evaluaciones. Mantener
   siempre incumbente válido. Aceptación: mejoras certificadas en varios n,
   distribuciones de resultados en al menos 10 semillas y tiempos medidos.
4. **M3 — Escala (implementada y comprobada hasta n=1000).** Filtro espacial,
   reanudación exacta, caché, warm starts por n, catálogo y procesos paralelos;
   37 tests, perfil comparativo y validación oficial offline en n=1000.
   El benchmark usa casos representativos y presupuesto corto; no se afirma una
   campaña competitiva completa de 1..1000. Evidencia en `scaling.md`.
   Plan original: broad phase espacial, warm starts por n,
   paralelismo entre puzzles, checkpoint y caché. Medir antes de añadir NumPy,
   SciPy, compilación o GPU. Aceptación: coste/beneficio documentado hasta n=1000,
   sin degradar mejores soluciones.
5. **M4 — Entrega local de portfolio preparada.** README consolidado, galería,
   gráfico de rendimiento, caso de estudio, informe de fracasos y ablations,
   notas de versión, guion de demo y revisión de procedencia. Apache 2.0 está
   preparada como propuesta; falta elección definitiva del propietario.
   La reproducción limpia se registra en `release-validation.md`; el CSV mantiene
   su contraste oficial. Publicación, release remota y envío quedan pendientes
   de solicitud del usuario, no se presentan como hechos consumados.

No prometer récords ni premios. Para un portfolio es valioso mostrar un resultado
modesto correcto y por qué una búsqueda no mejora al control. En la demo, incluir
45° explícitamente domina todas las muestras aleatorias: esto es una ablation
constructiva de referencia, no evidencia de eficacia de un optimizador general.
