# Memoria del proyecto tAilorPack Lab

| Dato | Información |
| --- | --- |
| Proyecto | Juego de geometría y laboratorio de empaquetado de cuadrados |
| Autora | Araceli Fradejas Muñoz |
| Origen | Competición Squares in Squares de Kaggle |
| Objetivo | Aprender, experimentar y construir un proyecto de portfolio que se pueda probar |
| Tecnologías | Python, JavaScript, HTML, CSS, SVG, Web Workers y Local Storage |
| Repositorio | https://github.com/AraceliFradejas/tailorpack-lab |
| Licencia | Apache 2.0 |
| Versión | App 0.2.0 · motor Python 0.1.0 · octubre de 2026 |
| App publicada | https://tailorpack-lab.vercel.app/ |

## 1 Contexto y motivación

Empecé tAilorPack al encontrar la competición Squares in Squares de Kaggle. Después de tAilorCode quería volver a experimentar con un problema concreto, con una parte técnica que pudiera comprobar y un resultado que tuviera sentido enseñar en mi portfolio.

La propuesta es colocar cuadrados unitarios dentro del menor cuadrado posible. Todos tienen el mismo tamaño, pero pueden moverse y girarse. Una distribución que parece mejor a simple vista puede tener un cruce muy pequeño y dejar de ser válida. Esa combinación de juego visual y comprobación matemática es lo que organiza el proyecto.

Mi intención inicial fue desarrollar un experimento reproducible en Python y entender las reglas antes de preparar una posible submission. Después amplié la idea con una app para jugar y ver qué hace la búsqueda. La competición sigue siendo el origen y una posible continuación; la app permite probar el proyecto sin entrar en Kaggle ni preparar un entorno de Python.

## 2 Objetivos y alcance

Quería conservar un punto de partida sencillo, comparar mejoras y poder repetir cada experimento. La rejilla cumple esa función: es fácil de entender y sirve para medir si la búsqueda aporta algo.

Los objetivos de esta primera versión son:

- Representar correctamente centros, ángulos y vértices de los cuadrados.
- Comprobar cruces y medir el contenedor.
- Comparar construcción geométrica, greedy y simulated annealing.
- Guardar semillas, presupuestos, resultados y checkpoints.
- Contrastar el CSV final con el evaluador oficial descargado de Kaggle.
- Crear un tablero que se pueda mover, girar y observar en el navegador.
- Explicar tanto las mejoras como los intentos que no mejoraron la rejilla.

El proyecto todavía no incluye un modelo entrenado, un servicio de IA, cuentas de usuario ni un servidor de partidas. La app trabaja en el navegador y guarda sus récords en el dispositivo.

## 3 Reglas y relación con Kaggle

Contrasté el problema en las páginas de descripción, evaluación, datos y reglas de la competición. El registro de fuentes y fecha de consulta está en [reglas verificadas](docs/verification.md).

El contrato revisado contempla puzzles de uno a mil cuadrados unitarios. Cada pieza se representa por su centro y su ángulo en radianes. Los interiores no pueden solaparse; el contacto está permitido. El contenedor se mide con los extremos de todos los vértices y permanece alineado con los ejes.

El CSV tiene las columnas `id,n,square_id,x,y,angle`. El lado no se envía: lo calcula la métrica. La puntuación suma `L/sqrt(n)-1`, de modo que un valor menor es mejor. Los puzzles omitidos reciben la penalización de la rejilla; se omite un puzzle completo, no piezas sueltas.

Preparé un adaptador que importa el notebook oficial v17 sin modificar su código y comprueba una huella de la versión revisada. Los archivos oficiales no están incluidos en el repositorio. Quien quiera repetir esa validación debe descargarlos de Kaggle y seguir la [guía](docs/official-validation.md).

Distingo tres pasos: generar una configuración, validarla offline con el evaluador oficial y recibir una respuesta de Kaggle. Solo se han realizado los dos primeros. El proyecto no tiene todavía una submission ni una posición en el leaderboard.

## 4 Del primer experimento a la búsqueda general

### La rejilla y el caso de cinco cuadrados

La rejilla coloca las piezas sin girarlas y usa un lado `ceil(sqrt(n))`. Para cinco cuadrados el lado es 3. Añadí una construcción con cuatro piezas en las esquinas y una central girada que permite reducirlo a aproximadamente 2,7071067822.

Incluí explícitamente el ángulo de 45°. Es una referencia geométrica preparada para comparar, no un hallazgo descubierto por las muestras aleatorias ni una fórmula inventada por este proyecto.

### Greedy y simulated annealing

La búsqueda general propone cambios en centros y ángulos. Greedy conserva las mejoras; annealing puede aceptar temporalmente un empeoramiento según la temperatura para explorar otras configuraciones. Una reparación intenta separar las piezas, y el mejor resultado válido se conserva aparte del estado de exploración.

Comparé diez semillas con el mismo presupuesto. En el experimento de diez cuadrados, la mejor semilla llegó a un lado de 3,9100797962 frente a 4 en la rejilla. Mejoraron tres semillas y la mediana siguió en 4.

Este resultado me sirve para mostrar que una búsqueda puede funcionar en un caso sin ser consistente. Conservar las otras semillas evita presentar el mejor intento como si fuera el resultado habitual. Los [resultados de búsqueda](docs/search-results.md) mantienen ese contexto.

## 5 Escala, reanudación y rendimiento

Comprobar todos los pares se encarece al aumentar las piezas: mil cuadrados implican 499.500 pares posibles. Incorporé un filtro espacial que descarta pares alejados antes de aplicar la comprobación geométrica detallada.

En la rejilla de mil piezas, el perfil guardado revisa 3.811 candidatos. En esa carga se midió una mejora aproximada de 85 veces en validación y 26 veces en reparación. Es un resultado del experimento concreto, no una aceleración garantizada para cualquier distribución. El peor caso continúa siendo cuadrático.

También preparé checkpoints con el generador aleatorio, el paso, la configuración actual, la mejor solución y el horizonte de búsqueda. La versión Python puede reanudar exactamente una ejecución compatible. La app web permite detener la búsqueda, pero no ofrece esa misma reanudación exacta.

El trabajo paralelo reparte puzzles y semillas entre procesos. Las ejecuciones secuencial y paralela comprobadas produjeron el mismo CSV. La prueba de escala utiliza tamaños representativos y presupuestos cortos; no equivale a una campaña larga sobre los mil puzzles.

## 6 La app y su identidad visual

Quería que la parte visible fuera algo que se pudiera probar, además de enseñar esquemas y números. El tablero permite seleccionar una pieza, moverla, girarla y ver inmediatamente si aparecen cruces.

La estética toma como referencia un cubo de Rubik: rojo, azul, verde, amarillo, naranja y blanco, con bordes oscuros y caras ligeramente redondeadas. El contorno azul identifica la selección y el magenta señala piezas que se cruzan. El color de una pieza sigue siendo parte de su identidad visual.

La página ofrece presets de cinco, diez, veinticinco y cien cuadrados, además de entrada manual hasta mil. Se puede volver a la rejilla, deshacer cambios, ajustar la vista y cargar las referencias de cinco y diez piezas. La búsqueda automática muestra sus avances sin bloquear el tablero.

El juego es una interpretación visual del problema de empaquetado; no implementa los giros de un cubo tridimensional. La inspiración estética no implica una relación oficial con la marca.

## 7 Organización técnica

He mantenido dos implementaciones con propósitos relacionados. Python reúne los experimentos reproducibles y la validación offline. JavaScript permite explorar el problema de forma interactiva. No doy por hecho que una semilla numérica produzca la misma trayectoria en ambos motores.

| Parte | Responsabilidad |
| --- | --- |
| `tailorpack/geometry.py` | Representación de piezas, vértices, SAT y filtro espacial |
| `tailorpack/solvers.py` y `search.py` | Construcción, movimientos, reparación y checkpoints |
| `tailorpack/benchmark.py` y `scale.py` | Comparación por semillas, caché y procesos |
| `tailorpack/official.py` | Adaptación aislada del evaluador oficial |
| `app/public/engine.js` | Geometría y exportación del navegador |
| `app/public/solver.js` y `worker.js` | Búsqueda incremental en segundo plano |
| `app/public/board-view.js` | Dibujo de las piezas en SVG |
| `app/public/metrics.js` | Análisis compartido de lado y cruces |
| `app/public/records.js` | Lectura y validación de récords locales |
| `app/public/app.js` | Eventos y coordinación de la interfaz |

Utilicé JavaScript vanilla porque el tablero no requiere un framework ni un backend. SVG permite dibujar las piezas, indicar su selección y mantener una imagen nítida. El Web Worker separa la búsqueda del hilo de la interfaz.

El guardado local comprueba los resultados al leerlos. Si hay datos corruptos o el navegador no permite almacenamiento, la app puede continuar. Un dato guardado no se considera un récord válido solo por tener un lado pequeño.

## 8 Validación y resultados conservados

La suite Python contiene 37 tests: 32 funcionan con la biblioteca estándar y cinco necesitan el notebook y las dependencias opcionales. Los 37 pasaron en el entorno local preparado; una ejecución sin ese entorno omite explícitamente los cinco oficiales. La app tiene 22 tests de geometría, búsqueda y estado.

GitHub Actions comprueba Python 3.11, 3.12 y 3.13 y ejecuta los tests y el build de la app. Las [ejecuciones públicas](https://github.com/AraceliFradejas/tailorpack-lab/actions) permiten consultar el resultado correspondiente a cada commit.

El candidato más reciente contiene veinte puzzles: n=1..16 y 100, 250, 500 y 1.000. Son 1.986 filas. Su [informe oficial offline](examples/m3-best/official-v17/official_validation.json) registra los puzzles aceptados y la huella del CSV exacto. La puntuación sobre el universo de mil puzzles es 28,7782488224, incluidas las penalizaciones por los puzzles omitidos.

La validación del navegador usa números de JavaScript y no sustituye la comprobación oficial. Las referencias incluidas en la app se generan desde el candidato guardado; una utilidad comprueba que no se hayan cambiado sus coordenadas por error.

En la revisión local se comprobó el uso con ratón y teclado, la aparición de cruces, deshacer, la búsqueda y una anchura móvil de 390 píxeles. Esa revisión de tamaño no sustituye una prueba en un dispositivo táctil físico.

## 9 Dificultades y decisiones

Una mejora muy pequeña puede desaparecer si la configuración tiene solapamientos. Por eso mantuve la validación separada de la búsqueda y conservé siempre una solución válida.

Otro problema fue mezclar demasiadas tareas en el controlador de la app. Separé dibujo, métricas y persistencia, y evité calcular dos veces los mismos cruces en cada actualización. También separé el tema del cubo del CSS base para poder modificarlo sin afectar al resto de la distribución.

La primera documentación estaba más orientada a una entrega técnica que a presentar mi proyecto. La revisé tomando como referencia Games Hub, KelseTS Maison y tAilorCode: una introducción personal, la demo visible, decisiones explicadas y esta memoria como documento del recorrido.

Los manifiestos de ZIP, preparativos de publicación y archivos temporales quedan fuera del repositorio. Mantengo los resultados pequeños de los experimentos porque permiten comprobar las cifras de la memoria. Los registros nuevos, builds, entornos y credenciales se excluyen mediante `.gitignore`.

## 10 Publicación

El repositorio público está en [AraceliFradejas/tailorpack-lab](https://github.com/AraceliFradejas/tailorpack-lab), con licencia Apache 2.0 y autoría de Araceli Fradejas Muñoz. La app se prepara para Vercel usando `app` como raíz, el comando `npm run build` y `dist` como carpeta de salida. No necesita variables de entorno.

La app está publicada en [tailorpack-lab.vercel.app](https://tailorpack-lab.vercel.app/), en el proyecto Hobby de mi cuenta Vercel y conectada al repositorio de GitHub. Se comprobó el acceso desde un navegador sin sesión de Vercel, la carga de referencias, los giros, los cruces, deshacer y la búsqueda en segundo plano. Las capturas siguientes proceden de esa URL pública el 24 de octubre de 2026.

![App publicada: diez cuadrados con la estética de cubo de colores](docs/images/rubik-desktop.png)

![Referencia de cinco cuadrados en la versión de Vercel](docs/images/rubik-five.png)

No se ha enviado ningún CSV a Kaggle.

## 11 Qué quiero ampliar

El siguiente trabajo de optimización consiste en mejorar los puntos de partida y añadir movimientos colectivos. Quiero comprobar mejoras repetidas en varios tamaños, con el mismo presupuesto y varias semillas.

Más adelante puedo probar una política pequeña que elija inicializaciones o movimientos. Primero necesito más trayectorias y separar los casos usados para entrenar de los usados para evaluar. La comparación debe incluir el coste de entrenamiento e inferencia. Actualmente el annealing es una heurística, no un modelo entrenado.

También queda probar el recorrido en dispositivos táctiles reales y ampliar las opciones para conservar y compartir configuraciones. Las ampliaciones se decidirán a partir de lo que aporte valor al juego y al experimento.

## 12 Qué me llevo del proyecto

El proyecto conecta una idea visual sencilla con cuestiones de geometría, precisión numérica y diseño de experimentos. Me ha servido para organizar una búsqueda que se pueda repetir y para distinguir una mejora ocasional de un método consistente.

La app hace visible esa diferencia: mover una pieza puede reducir el espacio y, al mismo tiempo, crear un cruce. Poder observarlo y corregirlo convierte el resultado técnico en algo que otra persona puede explorar.

## 13 Ampliación v0.2 · comparar dos motores

He conservado el motor web original y añadido una segunda estrategia con rejilla escalonada, disposición girada, reinicios y movimientos de grupos de piezas. También extendí la construcción de cinco cuadrados a cuatro bloques de esquina y una pieza central: permite preparar casos de 17 y 37 cuadrados.

El Laboratorio permite ejecutar ambos motores con el mismo tablero, semilla y presupuesto. Cada motor recibe sus propias propuestas; ejecutar la comparación duplica el total. La app conserva el mejor resultado recibido y marca como parciales las comparaciones interrumpidas.

La serie de diez semillas, nueve tamaños y controles con construcción compartida reúne 240 ejecuciones. La v2 mejora desde la rejilla en 5, 17 y 37; no mejora los otros seis tamaños. Cuando doy la misma construcción a ambos motores, las treinta parejas empatan. La v2 consume más tiempo. No puedo atribuir las mejoras a los movimientos colectivos ni presentar superioridad general.

La primera construcción pasaba las comprobaciones locales, pero el evaluador oficial dejaba algunos contactos como indecidibles. Añadí separación positiva entre las piezas de cada bloque y repetí los experimentos. El CSV corregido de nueve puzzles fue aceptado offline por el evaluador v17. El [informe v0.2](docs/search-v02.md) conserva protocolo, resultados, tiempos y validación; no se ha enviado a Kaggle.

Esta ampliación está implementada en el motor JavaScript y se puede reproducir desde Node. El motor histórico de Python y las referencias anteriores siguen conservados. No he conectado Gemma: primero he creado una comparación que permitirá medir si un futuro agente aporta una mejora.

## Autora

**© 2026 Araceli Fradejas Muñoz · tAilorPack**

Proyecto creado y dirigido por Araceli Fradejas Muñoz con asistencia de OpenAI Codex en desarrollo, pruebas y documentación. Los métodos matemáticos generales y las fuentes oficiales conservan su atribución, descrita en [procedencia](docs/provenance.md).

[GitHub](https://github.com/AraceliFradejas) · [LinkedIn](https://www.linkedin.com/in/araceli-fradejas-munoz-transformaciondigital/) · [X](https://x.com/AraceliFradejas) · [Medium](https://medium.com/@araceli.fradejas) · [YouTube](https://www.youtube.com/@aracelifradejasmunoz2758)
