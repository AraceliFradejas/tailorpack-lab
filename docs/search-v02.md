# v0.2 · Comparar antes de sustituir el motor

Quise avanzar desde la primera búsqueda hacia una versión con varios puntos de
partida y movimientos de grupos. Conservé el motor publicado como `solver-v1.js`,
sin cambiar sus bytes, para poder compararlo con la alternativa.

## Qué cambia

La v2 vive en JavaScript y se utiliza tanto en la app como en un experimento de
Node.js sin navegador. El motor histórico de Python permanece sin cambios. No se
puede identificar la misma semilla de JavaScript con una trayectoria de Python.

La nueva estrategia reparte el presupuesto en cuatro tramos. Empieza desde el
mejor estado válido entre el tablero recibido y la rejilla, prueba una rejilla
escalonada, una disposición girada y finalmente vuelve al mejor resultado. En
cada tramo enfría la búsqueda. Combina cambios de una pieza, traslaciones sin
giro y transformaciones rígidas de grupos de entre dos y cinco piezas cercanas.
La reparación posterior puede modificar las distancias del grupo: la rigidez se
refiere a la propuesta previa a esa reparación.

La v2 también prueba una construcción explícita para `n=4k²+1`: cuatro bloques
k×k en las esquinas y una pieza central girada 45°. Es una extensión del control
de cinco cuadrados del proyecto. No se atribuye a una búsqueda aleatoria, un
modelo de IA ni un nuevo récord matemático.

Con separación interna `g=1e-8`, cada bloque mide `b=k+(k-1)g`. El contenedor usa
`L=2b+1/sqrt(2)+g`. Los extremos diagonales del cuadrado central quedan separados
de las esquinas interiores de los bloques. Sin los márgenes, la fórmula ideal
es `2k+1/sqrt(2)`. Las piezas mantienen lado unitario.

## Presupuesto y comparación

Cada motor recibe **2.500 propuestas**, incluidas las construcciones y los
reinicios de v2. Una reparación fallida también consume una propuesta. Ambos
reciben una copia del mismo tablero y la misma semilla. Sus secuencias aleatorias
internas son diferentes porque sus operaciones lo son. El presupuesto no limita
por igual el tiempo ni el número de operaciones geométricas: la v2 valida cada
candidato reparado y selecciona grupos, lo que añade trabajo.

El botón **Comparar actual y nuevo** está en Laboratorio. Ejecuta primero v1 y
luego v2, con un solo worker: 5.000 propuestas totales si se eligen 2.500 por
motor. El tablero conserva el mejor resultado recibido, aunque el motor que se
ejecute después no lo supere. Las cifras de una ejecución detenida son parciales.
El motor por defecto sigue siendo v1; v2 es una opción experimental.

## Experimento guardado

Se revisaron inicialmente semillas 0–2 con 1.500 propuestas. La serie documentada
usa semillas **10–19**, nueve tamaños y 2.500 propuestas por motor, con annealing.
Es un experimento exploratorio; no se afirma significación estadística ni
superioridad general. Para 5, 17 y 37 también se repite la comparación dando la
misma construcción a ambos motores. En total son **240 ejecuciones y 600.000
propuestas**.

| n | Mediana v1 desde rejilla | Mediana v2 desde rejilla | Victorias v2 / 10 |
| --- | --- | --- | --- |
| 5 | 2,96030024 | ≈2,70710680 | 10 |
| 9 | 3 | 3 | 0: diez empates |
| 10 | 4 | 4 | 0: diez empates |
| 11 | 4 | 4 | 0: diez empates |
| 13 | 4 | 4 | 0: diez empates |
| 16 | 4 | 4 | 0: diez empates |
| 17 | 5 | ≈4,70710682 | 10 |
| 20 | 5 | 5 | 0: diez empates |
| 37 | 7 | ≈6,70710685 | 10 |

Los decimales exactos se conservan en [benchmark.json](../examples/web-v02/benchmark.json).
**Con la construcción compartida, los dos motores empatan en las treinta parejas.**
La evidencia atribuye las mejoras observadas a esa construcción inicial; no
establece una ventaja de los movimientos colectivos o de los reinicios.

Los [tiempos](../examples/web-v02/timings.json) incluyen inicialización y búsqueda,
medidos secuencialmente con Node 22.23.2 en macOS arm64. Se conservan separados del
informe determinista; dependen de la máquina y la carga. La v2 requiere más tiempo
en esta serie. No se está presentando una comparación a igual tiempo de ejecución.

## Precisión y validación

La primera construcción dejaba contactos exactos entre piezas de un mismo bloque.
Pasaba el SAT de JavaScript y la comprobación float independiente de Python, pero
el evaluador oficial v17 marcó n=17 y n=37 como «Overlap undecidable at max
precision». Se añadió separación positiva interna y se repitió la serie completa.
Ese margen es una decisión de implementación, no una tolerancia oficial.

La comprobación Python lee de nuevo el CSV, verifica cobertura, IDs, huella del
archivo, presupuestos emparejados y hashes del motor, y comprueba su geometría.
Su [informe](../examples/web-v02/python-validation.json) es independiente del
solver JavaScript, pero sigue usando floats. El [informe oficial v17](../examples/web-v02/official-v17/official_validation.json)
acepta los nueve puzzles del CSV corregido. Registra 1,1533284484 como suma del
subconjunto y 28,6874957186 sobre el universo de mil puzzles, con penalizaciones
para los omitidos. Es una comprobación offline, no un score recibido de Kaggle. Generar otra configuración en la app no
hereda la validación del archivo guardado.

El candidato de este experimento contiene nueve puzzles, no reemplaza el
candidato histórico combinado ni las referencias de la app. No hay envío a
Kaggle ni un nuevo score recibido del servidor.

## Reproducir

Desde la raíz del repositorio, con Node.js 22+ y Python 3.11+:

```sh
node app/tools/benchmark.mjs --ns 5,9,10,11,13,16,17,20,37 \
  --seeds 10,11,12,13,14,15,16,17,18,19 --budget 2500 --out runs/web-v02
python3 tools/check_web_benchmark.py --folder runs/web-v02 --out runs/web-v02/python-validation.json
npm test --prefix app
npm run build --prefix app
```

Las fuentes guardadas en el informe deben coincidir para comprobarlo. Los
resultados y el CSV se contrastan entre dos ejecuciones; los tiempos no deben
compararse byte a byte. La [guía oficial](official-validation.md) explica cómo
repetir el paso adicional con los archivos externos de Kaggle.

## Siguiente decisión

Antes de introducir Gemma, quiero obtener mejoras de búsqueda que sobrevivan a
un inicio compartido y a presupuestos comparables. El experimento deja una base
para que un futuro agente seleccione estrategias y evalúe resultados, pero no
se ha conectado un modelo ni se ha creado un servicio de IA en esta versión.
