# tAilorPack Playground

Juego visual de empaquetado de cuadrados, publicado en **[Vercel](https://tailorpack-lab.vercel.app/)**. Aplicación
estática en HTML/CSS/JavaScript, sin dependencias de ejecución, cuentas ni backend.

Tema visual inspirado en un cubo de colores: seis tonos, marcos negros y pegatinas
con relieve. La selección lleva un borde azul y los cruces un contorno discontinuo
magenta, para distinguirlos de las piezas de color rojo.

![Vista real del juego publicado](../docs/images/rubik-desktop.png)

## Jugar y desarrollar

Node.js 22 o posterior. Desde esta carpeta:

```sh
npm ci
npm test
npm run dev
```

Abrir la dirección que imprime el servidor, normalmente `http://127.0.0.1:4173`.
No abrir `index.html` como archivo: los módulos, JSON y Web Worker necesitan HTTP
o HTTPS. `npm run build` copia los archivos públicos a `dist/`.

- Arrastrar con ratón o puntero táctil; seleccionar y girar con el deslizador.
- Flechas para mover; Q/E para girar; Shift amplía el paso. Deshacer y ajustar vista.
- Retos de 1 a 1.000 cuadrados; presets 5,10,25,100. Etiquetas hasta 50 piezas.
- Lado del contenedor, reducción frente a la rejilla, ocupación y cruces en directo.
- Motor local greedy/annealing en un Web Worker, con semilla y presupuesto.
- Detener una búsqueda conserva el mejor estado recibido; no es una pausa con
  reanudación exacta como el motor Python. Volver a ejecutar inicia otra búsqueda.
- Referencias precargadas de n=5 y n=10, derivadas del candidato del portfolio.
- Mejor lado guardado en este navegador con localStorage. No es un ranking global.
- Exportar el puzzle completo a CSV con las seis columnas verificadas de Kaggle.

## Subir a Vercel

1. Publicar los archivos de la app en un repositorio de GitHub.
2. En Vercel, crear un proyecto e importar ese repositorio.
3. Si se subió **todo tAilorPack**, elegir **Root Directory: `app`**. Si se subió
   **solo el contenido de esta carpeta**, dejar Root Directory en la raíz.
4. **Framework Preset: Other**, **Build Command: `npm run build`**,
   **Output Directory: `dist`**. `vercel.json` ya declara estos ajustes y encabezados.
5. Desplegar. No necesita variables de entorno, API keys ni base de datos.

Los ajustes de Root Directory y Output Directory siguen la
[documentación de Vercel](https://vercel.com/docs/builds/configure-a-build).
El despliegue remoto no se ha realizado desde esta tarea. Se comprobó el build
local y el servidor de prueba utiliza los mismos encabezados CSP declarados.

## Qué significa la validación

La app calcula solapamientos con floats y SAT. Las referencias del proyecto se
validaron offline con el notebook oficial v17; sus hashes y contexto están en
`public/references.json`. Eso no certifica una configuración después de editarla
ni una solución nueva del motor web.

El RNG de JavaScript es determinista en esta implementación, pero distinto del
de Python: la misma semilla no produce la misma trayectoria. En n=5 se usa una
familia constructiva explícita como inicio. No se afirma que el solver descubra
esa construcción, supere récords o mejore todos los puzzles.

El CSV es un candidato local, no una submission enviada. Para usarlo en Kaggle,
pasar el archivo serializado por el evaluador oficial y revisar las reglas vigentes.
No se añade límite de tiempo ni penalización de juego a las reglas oficiales.

## Estructura y QA

`public/`: controlador `app.js`, dibujo `board-view.js`, métricas `metrics.js`,
persistencia `records.js`, geometría, solver, worker y referencias. El tema visual
está separado en `cube.css`, sobre los estilos base legibles de `style.css`.
`tests/`: 22 tests del motor y estado web, incluida una rejilla de mil cuadrados.
`tools/`: servidor local y build estático. [Comprobaciones realizadas](docs/qa.md).
La [vista móvil](docs/preview-mobile.jpg) se comprobó a 390 px sin desbordamiento
horizontal. Ratón y teclado se probaron en el navegador; no se probó un dispositivo
táctil físico. Autora: Araceli Fradejas Muñoz (@AraceliFradejas). Licencia Apache 2.0;
consultar `LICENSE` y `NOTICE` en la raíz del repositorio.

Las referencias se regeneran desde la raíz del portfolio con
`python3 tools/sync_references.py`; `--check` verifica que no haya divergencias
respecto al candidato validado. La entrega independiente de la app ya las incluye.

## Motores y comparación · v0.2

En Laboratorio se puede elegir v1 o v2 y comparar ambos con el mismo tablero,
semilla y presupuesto por motor. La v1 sigue siendo la opción por defecto. La v2
es experimental: añade inicios, reinicios, grupos y construcciones explícitas;
no demuestra superioridad general. Ver [resultados y protocolo](../docs/search-v02.md).
La comparación usa un solo worker, ejecuta primero v1 y después v2 y conserva el
mejor estado de ambos. Las cifras al detenerla son parciales.

Desde la raíz, `node app/tools/benchmark.mjs --out runs/web-v02` reproduce la serie
definida por defecto. `python3 tools/check_web_benchmark.py` comprueba la evidencia
guardada; `--folder runs/web-v02` comprueba una nueva ejecución.
