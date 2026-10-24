# GitHub y primera versión

La entrega local está preparada para un repositorio llamado **tailorpack-lab**,
con nombre visible **tAilorPack Lab**, en la cuenta `AraceliFradejas`.
Publicar el contenido descomprimido de esta carpeta como raíz, con README visible;
el ZIP es un medio de transporte, no el contenido principal del repositorio.

Descripción propuesta:

> Interactive square-packing playground with geometric optimization, reproducible Python experiments, and offline validation against Kaggle's official metric.

Temas sugeridos: `python`, `computational-geometry`, `optimization`,
`simulated-annealing`, `reproducible-research`, `kaggle`.

## Revisión final

1. Licencia Apache 2.0 aplicada con autoría de Araceli Fradejas Muñoz. Ver `LICENSE` y `NOTICE`.
2. Ejecutar `python3 tools/check_release.py` y los tests del README.
3. Subir código, tests, docs, figuras y ejemplos. Excluir descargas de Kaggle,
   credenciales, entornos y `runs/`; el `.gitignore` cubre estas rutas.
4. Tras crear el repositorio, comprobar la CI real antes de poner un badge verde.
5. Preparar una release `v0.1.0` usando [las notas](release-notes.md).

## Presentación correcta

M0 y M1 completas; M2 implementada con calidad abierta; M3 comprobada hasta n=1000;
M4 preparada localmente. Decir «validado offline con el notebook oficial v17».
No decir «submission aceptada», «récord», «top de Kaggle» ni «todos los puzzles
optimizados». Usar el [caso de estudio](portfolio-case-study.md) como texto base
y la galería del README como vista inicial.

Destino público autorizado por la autora el 24-10-2026:
https://github.com/AraceliFradejas/tailorpack-lab. No se ha publicado una release.
