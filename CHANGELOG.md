# Historial

## Investigador experimental — 24-10-2026

- Orquestador Node con dos herramientas permitidas, contabilidad de propuestas,
  rechazo de duplicados y límite de decisiones; sin ejecución de código del modelo.
- Controles programados reproducidos con los motores reales y etiquetados sin IA.
- Adaptador local Ollama con JSON estructurado y ocho tests nuevos. No se ha
  ejecutado Gemma ni se afirma mejora de IA; configuración y evaluación pendientes.
- Guía y memoria ampliadas; comprobador independiente de controles en Python.

## App 0.2.0 — 24-10-2026

- Motor web v1 conservado sin cambios y v2 experimental con inicios alternativos,
  reinicios y movimientos colectivos; construcción explícita para 4k²+1 piezas.
- Comparación en Laboratorio con el mismo tablero, semilla y presupuesto por motor.
- 240 ejecuciones reproducibles; las mejoras observadas proceden de la construcción,
  sin ventaja demostrada con inicio compartido ni en los otros seis tamaños.
- Corregidos contactos exactos indecidibles mediante separación positiva interna.
  Nueve puzzles aceptados offline por el evaluador oficial v17; sin envío a Kaggle.
- 22 tests web, comprobación independiente en Python e informe en `docs/search-v02.md`.
- README y memoria ampliados; motor histórico de Python sin cambios.

## Preparación de GitHub — 24-10-2026

- Propuesta de nombre tAilorPack Lab / `tailorpack-lab`.
- Separados dibujo, métricas compartidas y registros locales del controlador web.
- Estilos base legibles y tema visual separado; avisos coherentes con los colores.
- Validación de entradas del solver, cinco regresiones web nuevas y verificación
  de la procedencia exacta de las referencias del navegador.

## Actualización visual — 24-10-2026

- Playground con seis colores, marco negro, pegatinas con relieve, icono y controles
  inspirados en un cubo de colores. Selección azul y aviso de cruces discontinuo.
- Capturas de escritorio y móvil actualizadas; geometría y optimizador sin cambios.

## 0.1.0 — Entrega de portfolio, 23-10-2026

- Reglas y formato contrastados en Kaggle; adaptador del notebook v17 con hash fijado.
- Rejilla, construcción n=5, búsqueda greedy/annealing y comparación de diez semillas.
- Mejora de búsqueda n=10: 4 a 3,9100797962; éxito en 3/10 semillas a ese presupuesto.
- Filtro espacial, referencia exhaustiva, checkpoints, caché, catálogo y procesos.
- Prueba de infraestructura hasta n=1000 y candidato combinado validado offline.
- 37 tests en la suite; galería, informe de portfolio y preparación de publicación.
- Playground web preparado para Vercel: juego manual, optimizador en worker,
  referencias precargadas, exportación CSV y diez tests adicionales de JavaScript.

El repositorio y la app están publicados en GitHub y Vercel con Apache 2.0.
No hay envío a Kaggle. Sigue abierta la meta de mejorar la búsqueda de forma
consistente en varios puzzles fuera de las construcciones preparadas.
