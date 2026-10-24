# M1 — Contrato oficial completado

23-10-2026. Se descargaron [sample](https://www.kaggle.com/competitions/squares-in-squares/data)
y [notebook oficial v17](https://www.kaggle.com/code/metric/squares-in-squares)
desde la sesión del navegador que ya tenía acceso. No se enviaron predicciones.

## Verificaciones realizadas

- Sample original: 12.872.271 bytes, 500.500 filas, puzzles 1..1000 con exactamente
  n filas por puzzle, id consecutivo global y square_id consecutivo por puzzle.
- Cabecera exacta: `id,n,square_id,x,y,angle`. Prefijo n=1..16 igual a la rejilla local.
- Código completo extraído de la única celda del notebook v17; revisión de parser,
  SAT float, intervalos, puntuación y salida de detalles. Sin modificar el código.
- CSV leído como cadenas para preservar sus literales. Se llamó `score()` con un
  DataFrame sintético que enumera n=1..1000, ya que esa columna fija el universo
  de puntuación. No es un `solution.csv` oficial descargado.
- Los 16 puzzles de rejilla y los 16 del candidato fueron aceptados offline.
  Se verificó `L` y la razón de aceptación por puzzle; el score por sí solo no
  demuestra validez porque los rechazos reciben la penalización de rejilla.
- Regresiones contra el notebook: contacto, solapamiento 1e-12, IDs duplicados,
  filas incompletas, NaN/inf/expresiones/overflow, n fuera de rango y puzzles omitidos.
- **23 tests correctos** con dependencias opcionales; la prueba del punto de
  entrada oficial se ejecutó además como CLI con sus cuatro procesos originales.

| Resultado | Rejilla 1..16 | Candidato 1..16 |
|---|---:|---:|
| Suma de puzzles entregados | 2.1667512492977705 | 2.035765420261864 |
| Score offline sobre universo 1..1000 | 28.937669916550586 | 28.80668408751468 |

El resto de puzzles recibe penalización de ausencia. No son scores recibidos del
servidor ni posiciones del leaderboard. La mejora viene solo de n=5.

## Versiones y reproducción

Entorno probado: pandas 2.2.3, mpmath 1.4.1; Python registrado en los informes.
Las versiones de dependencias son las probadas localmente, no una afirmación
sobre las instaladas en los servidores de Kaggle.

SHA-256 sample:
`a7f736d6cc72975459732a15d6ce6ae6588ad97d0c84f4d26905fd31ec09c74c`.

SHA-256 código extraído v17 (kernel version 360167936):
`312458227c78f56bd5e2eec3dc5fbb8787989422bbf72ce66c3c290048e89733`.

Descargar los dos archivos desde Kaggle a `data/official/` (excluido de Git).
El adaptador rechaza fuentes con otro hash hasta revisarlas.

```sh
python3 -m pip install -r requirements-official.txt
python3 -m tailorpack.official \
  --notebook data/official/squares-in-squares.ipynb \
  --sample data/official/sample_submission.csv \
  --candidate examples/demo/candidate_NOT_VALIDATED.csv \
  --out runs/official-v17
TAILORPACK_METRIC_NOTEBOOK=data/official/squares-in-squares.ipynb \
  python3 -m unittest discover -s tests -v
```

Sin esa variable, cinco regresiones oficiales se omiten expresamente; los demás
tests siguen siendo ejecutables con la biblioteca estándar. La CI pública no
descarga automáticamente archivos sujetos al acceso de Kaggle.

Informes guardados: `examples/official-v17/official_validation.json`,
`examples/official-grid-v17/official_validation.json` y respectivos
`submission_details.csv`. El candidato exacto se identifica por su SHA-256.
La extracción temporal no redistribuye el notebook. Su licencia publicada es
Apache 2.0; antes de incorporarlo al repositorio habría que preservar atribución
y licencia. Revisar cambios antes de un envío real.
