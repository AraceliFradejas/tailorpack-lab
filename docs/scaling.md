# M3 — Escala, reanudación y ejecución paralela

Implementada y comprobada el 23-10-2026 hasta **n=1000**, con casos representativos
10,100,250,500,1000. Esto acredita infraestructura en esa escala, no una búsqueda
competitiva de todos los 1.000 puzzles ni mejoras nuevas en puzzles grandes.
La calidad pendiente de M2 sigue siendo un trabajo independiente.

## Cambios

- Validación: cuadrícula espacial de AABBs para descartar pares lejanos antes del
  SAT. La referencia exhaustiva sigue disponible con `backend="all-pairs"`.
- Reparación: de un par se obtiene una cota inferior del factor de expansión.
  Para dos cuadrados unitarios separados una distancia r entre centros, al menos
  un eje proyecta r/sqrt(2), y la suma de semianchos proyectados no supera sqrt(2).
  Por tanto su umbral de expansión no supera `(2+sqrt(2)*margin)/r`. Los pares
  más alejados que el radio derivado no pueden aumentar el factor ya conocido.
  Una cuadrícula enumera los cercanos. Se amplía el radio por 1e-12 para absorber
  redondeo; esto no es una tolerancia oficial de solapamiento.
- Reanudación: JSON con configuración, hash del motor, paso, estado del RNG
  (incluida su caché gaussiana), estado actual e incumbente. Reemplazo atómico
  después de escribir el nuevo archivo. No es una garantía ante pérdida de energía.
- Caché: un checkpoint completo evita repetir propuestas. Cambios en motor,
  presupuesto o configuración se rechazan. Para aumentar presupuesto, crear otra
  carpeta e iniciar desde el mejor CSV; la reanudación exacta mantiene fijo el
  horizonte total para no cambiar la temperatura retrospectivamente.
- Paralelismo: procesos independientes por puzzle/semilla; solo el proceso padre
  actualiza el catálogo `best.json`, conservando el menor lado localmente válido.
- Warm start: CSV previo y catálogo del propio run. Cada trabajo guarda su inicio
  para que una reanudación no cambie por mejoras posteriores del catálogo.
  Un inicio peor que M0 se descarta. El runner exporta los n solicitados; para
  conservar otros n hay que unir incumbentes, como en `examples/m3-best/`.

## Medición de geometría

Medianas de tres repeticiones sobre rejillas alineadas, mismo equipo y entorno
registrado en `examples/scale-m3/profile.json`. Valores observados, sujetos a carga
y hardware; no extrapolar a configuraciones densas o a todo el optimizador.

| n | Todos los pares | Pares de validación espacial | Aceleración validación | Aceleración reparación |
|---:|---:|---:|---:|---:|
| 10 | 45 | 22 | 1,40x | 0,76x |
| 100 | 4.950 | 342 | 9,70x | 3,09x |
| 250 | 31.125 | 907 | 22,03x | 6,99x |
| 500 | 124.750 | 1.868 | 43,12x | 13,56x |
| 1000 | 499.500 | 3.811 | 84,89x | 25,64x |

Para n pequeño la cuadrícula puede costar más que recorrer todos los pares.
Las dos reparaciones produjeron exactamente los mismos cuadrados en los cinco
casos. Los tests también comparan layouts aleatorios rotados y búsquedas completas.
En el peor caso, con muchos cuadrados concentrados o radio muy grande, el coste
sigue siendo cuadrático; no se afirma complejidad lineal universal.

## Ejecución real y resultados

10 trabajos: cinco valores de n × semillas 0 y 1, 30 propuestas por trabajo.
Warm start desde M2 para n=10, rejilla para los otros cuatro puzzles.
Es un smoke benchmark de infraestructura, no una campaña de optimización larga.

- Dos procesos: 1,045 s; un proceso: 1,864 s, medidos en ejecuciones distintas.
  Aproximadamente 1,78x en esta muestra; los tiempos no son comparaciones aisladas
  ni garantizan aceleración para tareas cortas o equipos diferentes.
- Segunda ejecución: 10/10 trabajos recuperados de caché, sin repetir propuestas.
- CSV secuencial y paralelo idénticos byte a byte.
- **37 tests correctos**, incluidos los cinco del notebook oficial. La prueba
  de reanudación interrumpe a 57/150 propuestas y compara el resultado completo
  con una ejecución ininterrumpida. No se usa pickle para cargar checkpoints.
- El evaluador oficial v17 aceptó los cinco puzzles de escala, incluido n=1000.
  También aceptó el candidato combinado de **20 puzzles / 1.986 filas**: M2 en
  n=1..16 más 100,250,500,1000. Score offline total: **28.77824882235171**.
  Coincide con M2: añadir soluciones de rejilla sustituye penalizaciones iguales.
  M3 conserva las mejoras n=5/n=10; no obtuvo una mejora nueva de score.

Evidencias en `examples/scale-m3/` (mediciones, ejecuciones, validación oficial) y
`examples/m3-best/` (candidato combinado, procedencia y validación oficial).
Checkpoints y catálogos voluminosos quedan en `runs/`, excluidos de Git y del ZIP.
No se enviaron predicciones ni se publicó nada.

## Reproducir

```sh
python3 -m tailorpack.profile_scale --out runs/profile-scale.json
python3 -m tailorpack.scale --ns 10 100 250 500 1000 --seeds 0 1 \
  --evaluations 30 --workers 2 --checkpoint-every 10 \
  --warm-start examples/m2-best/candidate_NOT_VALIDATED.csv --out runs/scale
```

Repetir el segundo comando recupera los trabajos completos; si se interrumpió,
continúa desde el último checkpoint guardado. Solo cambia `--workers 1` para
usar ejecución secuencial, manteniendo carpeta/configuración. Para medir ejecución
secuencial desde cero usar otra carpeta. Para repetir la validación oficial:

```sh
python3 -m tailorpack.official \
  --notebook data/official/squares-in-squares.ipynb \
  --sample data/official/sample_submission.csv \
  --candidate examples/m3-best/candidate_NOT_VALIDATED.csv \
  --out runs/m3-official
```

Siguen aplicando las dependencias y acceso de Kaggle descritos en
`official-validation.md`. M3 no necesita NumPy, SciPy, GPU ni dependencias nuevas.
Siguiente paso de portfolio: M4, presentación y preparación de publicación; para
mejorar resultados competitivos, continuar M2 con movimientos colectivos y más
inicializaciones antes de gastar presupuestos grandes en n alto.
