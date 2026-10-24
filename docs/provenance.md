# Procedencia, autoría y licencia

## Código y figuras de esta entrega

Los módulos `tailorpack/`, tests y utilidades se escribieron para este proyecto.
El SAT, simulated annealing y la rejilla son técnicas matemáticas generales;
no se atribuye al proyecto su invención. La construcción n=5 se presenta como
referencia geométrica, no como récord ni hallazgo original.

Las figuras de `docs/assets/` se generan con `python3 -m tailorpack.portfolio`
desde los CSV y JSON guardados. Los SVG no dependen de datos remotos. Sus PNG
son renderizaciones de esos SVG, preparadas para verse en GitHub. No incluyen
fotografías, logotipos ajenos, fuentes descargadas ni imágenes de terceros.

## Material oficial externo

El [notebook oficial](https://www.kaggle.com/code/metric/squares-in-squares)
mostró licencia Apache 2.0; el [sample](https://www.kaggle.com/competitions/squares-in-squares/data)
mostró CC0 en Data. No se redistribuyen ninguno de los dos archivos. El adaptador
comprueba un hash del código extraído antes de importarlo localmente, sin modificarlo.
Los informes contienen resultados numéricos de ejecuciones y hashes, no el notebook.
Acceso y redistribución deben seguir las reglas vigentes de Kaggle.

Las dependencias opcionales pandas y mpmath se instalan aparte; sus fuentes,
binarios y ruedas no se incluyen. El núcleo usa la biblioteca estándar de Python.

## Autoría y licencia

Copyright © 2026 Araceli Fradejas Muñoz (@AraceliFradejas).
Proyecto creado por Araceli Fradejas Muñoz con asistencia de OpenAI Codex.
La autoría del proyecto no implica la invención de los métodos matemáticos
ni la propiedad de las fuentes oficiales de Kaggle.

El código, documentación y figuras propias se publican bajo [Apache 2.0](../LICENSE),
autorizada por la autora el 24-10-2026. El texto procede de la
[fuente oficial de Apache](https://www.apache.org/licenses/LICENSE-2.0.txt).
Consultar también [NOTICE](../NOTICE). Las fuentes externas conservan su atribución
y sus condiciones; revisar de nuevo las obligaciones del concurso para una solución premiada.

## Alcance de la publicación preparada

Incluye código, documentación, figuras propias, candidatos e informes pequeños.
Excluye datos descargados, credenciales, entornos, cachés y checkpoints de runs.
Repositorio público: https://github.com/AraceliFradejas/tailorpack-lab.
No se ha publicado una release ni enviado una predicción. La validación offline no afirma aceptación por Kaggle.
