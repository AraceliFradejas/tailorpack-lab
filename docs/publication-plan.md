# tAilorPack Lab — Revisión y publicación

24-10-2026. Destino propuesto: `AraceliFradejas/tailorpack-lab`.

Descripción preparada para GitHub:

> Interactive square-packing playground with geometric optimization, reproducible Python experiments, and offline validation against Kaggle's official metric.

## Revisión aplicada

| Hallazgo | Cambio |
|---|---|
| El controlador mezclaba dibujo SVG, geometría y persistencia | `board-view.js`, `metrics.js` y `records.js` separados |
| Guardar y dibujar recalculaban los mismos cruces | Un análisis compartido por actualización |
| Los registros locales se aceptaban sin validar su geometría | Comprobación de configuración y lado al leer; tolerancia a almacenamiento corrupto o deshabilitado |
| El solver podía fallar tarde con un número incorrecto de piezas | Validación explícita de cantidad, coordenadas, semilla y tamaño de lote |
| CSS compacto con el tema superpuesto al final | CSS legible; tema en `cube.css` cargado después de la base |
| Los avisos seguían hablando de piezas rojas | Texto coherente con el contorno magenta |
| Las referencias del navegador dependían de una copia manual | Generador `sync_references.py` y comparación exacta en el comprobador de entrega |

No se migró a React/Next ni se añadieron servicios: una app estática sigue siendo
adecuada para este juego y despliega en Vercel sin backend. Tampoco se cambiaron
los algoritmos Python ni los resultados históricos para maquillar métricas.

Verificación: 15 tests web correctos, build correcto; suite Python con 32 tests
correctos y cinco oficiales opcionales omitidos en la ejecución sin dependencias.
Las referencias mantienen el hash y geometría del candidato evaluado.

## GitHub

Subir una sola raíz con `README.md`, `tailorpack/`, `app/`, `tests/`, `tools/`,
`docs/`, `examples/` y `.github/`. Los ZIP son entregables, no el contenido del
repositorio. `runs/`, `app/dist/`, entornos y descargas están excluidos.
Se propone un primer commit local en `main`. La visibilidad y licencia definitiva
se decidirán con el propietario; Apache 2.0 sigue preparada como propuesta.

El conector permite consultar la cuenta y trabajar con repositorios existentes,
pero no expone creación de repositorios. El navegador mostró la pantalla de inicio
de sesión al abrir `https://github.com/new`; no se han introducido credenciales ni
creado un repositorio remoto durante esta revisión.

## Kaggle: participar sí, prometer competitividad no

Yo publicaría primero un notebook reproducible explicando control, mejoras,
fracasos y validación. Después haría una primera submission autorizada para medir
la integración real con la plataforma. El candidato actual es una base de aprendizaje.

El 24-10-2026 el [leaderboard visible](https://www.kaggle.com/competitions/squares-in-squares/leaderboard)
mostraba a su líder con **22.2247581510**. El candidato local registra
**28.77824882235171** en el universo offline de 1.000 puzzles. Menor es mejor:
hay una distancia importante. Esta comparación orienta el trabajo; no asigna
posición al candidato ni sustituye un score del servidor.

## IA que aporte una mejora medible

No añadiría un chatbot como requisito de esta primera publicación. El annealing
actual es una heurística de optimización, no un modelo entrenado ni un LLM.

Para una segunda versión, probaría **selección aprendida de inicializaciones o
movimientos**. La política propone; la geometría y el evaluador siguen decidiendo
si la configuración es válida. Plan de experimento, todavía sin implementar:

1. Registrar trayectorias de búsquedas y ampliar los pocos tamaños explorados.
2. Entrenar una política pequeña para elegir inicio o tipo de movimiento, con
   puzzles y semillas de validación separados de entrenamiento.
3. Comparar contra annealing, greedy y controles constructivos con igual presupuesto
   de propuestas; registrar también coste de entrenamiento e inferencia.
4. Medir exceso por n, tasa de validez y dispersión entre semillas, no solo la mejor.
5. Conservar un incumbente válido y certificar el CSV final con el evaluador oficial.

Los datos actuales son demasiado limitados para afirmar que entrenar un modelo
será útil. Antes de ese salto, movimientos colectivos y mejores inicializaciones
pueden dar mejoras con menos complejidad. Si la política no supera los controles,
documentarlo y mantener el solver simple.
