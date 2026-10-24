# tAilorPack v0.1.0 — Reproducible square packing

Primera entrega de portfolio: desde una rejilla de control hasta una búsqueda
geométrica con evidencia reproducible y validación offline del CSV.

## Incluye

- Construcción n=5: lado 3 a 2,7071067822.
- Annealing n=10: lado 4 a 3,9100797962; tres éxitos entre diez semillas.
- Filtrado espacial, checkpoints JSON, caché, catálogo y ejecución paralela.
- 37 tests y definición de CI para Python 3.11–3.13.
- Candidato combinado de veinte puzzles, validado con la métrica oficial v17.
- Galería, informe de resultados, intentos fallidos y comandos de reproducción.

## Límites

No se ha enviado a Kaggle ni se afirma ranking u optimalidad. La mejora de calidad
en varios puzzles sigue pendiente. Las mediciones de escala son sobre casos
representativos, no una campaña competitiva completa. La licencia definitiva debe
confirmarse antes de publicar esta release. Estas notas son un borrador local
para publicación posterior, no una release ya publicada.
