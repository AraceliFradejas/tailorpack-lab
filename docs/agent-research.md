# Investigador experimental · preparación de Gemma

Quise dar el siguiente paso sin confundir un modelo con el optimizador. El
investigador elige experimentos; los motores existentes colocan las piezas y
comprueban su geometría. La elección se devuelve como una instrucción JSON
pequeña, no como un programa que se ejecuta.

## Estado real

- Orquestación y herramientas implementadas en Node.js.
- Dos políticas programadas ejecutadas sobre los motores reales, sin IA.
- Adaptador de Ollama preparado para un modelo instalado localmente.
- Pruebas del transporte con respuestas de ejemplo; no son inferencias de Gemma.
- **No se ha ejecutado Gemma, entrenado un modelo ni demostrado una mejora de IA.**

No se encontró Ollama ni un endpoint configurado durante esta preparación. La
instalación o elección de proveedor queda pendiente. La app pública sigue usando
sus motores locales v1/v2; no se publica un servidor de inferencia en Vercel.

## Qué puede hacer

La política recibe número de piezas, lado inicial y mejor lado observado,
presupuesto restante, semillas permitidas y resultados de los experimentos ya
completados. Solo puede elegir:

1. `run_experiment`: motor v1/v2, una semilla permitida y un presupuesto válido.
2. `finish`: terminar la campaña.

Cada experimento empieza desde la misma rejilla. El mejor estado de la campaña
se conserva aparte. No se usan las respuestas del modelo como medidas del lado,
ni se aceptan coordenadas que el modelo invente como resultado de una búsqueda.

El límite global se reserva antes de ejecutar una herramienta; un reinicio del
solver forma parte de su presupuesto de propuestas. Las instrucciones inválidas
y las repeticiones se rechazan. También hay un máximo de decisiones, de modo que
una política que insista en errores no puede prolongar indefinidamente el bucle.

Las herramientas no incluyen terminal, edición de código, navegación, publicación
ni envío a Kaggle. Un fallo del proveedor termina la campaña con estado de error
y conserva el mejor resultado disponible. No se cambia silenciosamente a una
política programada fingiendo que el modelo ha funcionado.

## Controles ejecutados

Dos campañas de n=17, con 10.000 propuestas totales, máximo 2.500 por experimento,
hasta ocho decisiones y semillas disponibles 10, 11, 12 y 13:

| Política | Qué decide | Propuestas consumidas | Mejor lado |
| --- | --- | --- | --- |
| Control fijo | Siempre v1, recorriendo semillas | 10.000 | 5 |
| Control alternado | Alterna v1 y v2, con parejas de semillas | 10.000 | 4,7071068202 |

El control alternado utiliza v1/v2 con semillas 10 y 11; el fijo utiliza v1 con
las cuatro semillas. Tienen el mismo límite total y conjunto de semillas
permitidas, no una secuencia de experimentos idéntica. Ambos informes marcan
`modelExecuted: false` y cero intentos de inferencia.

La diferencia procede de la construcción explícita de v2 para diecisiete piezas.
**No es una victoria de un agente inteligente.** Es una comprobación del circuito
que un modelo podría utilizar después. No hay una evaluación estadística nueva
sobre múltiples tamaños ni una comparación con Gemma.

- [Informe del control alternado](../examples/agent-v03-control/report.json).
- [Informe del control fijo](../examples/agent-v03-fixed/report.json).
- Los tiempos de decisión y de solver se guardan por separado en cada carpeta.

La geometría y los IDs del CSV se comprueban independientemente en Python.
Estos dos CSV nuevos conservan estado de candidato local: no se ha ejecutado el
evaluador oficial sobre ellos ni se ha enviado una submission. La validación
oficial del experimento v0.2 no se hereda automáticamente.

## Reproducir sin instalar un modelo

Desde la raíz, con Node.js 22+ y Python 3.11+:

```sh
node app/agent/run.mjs --policy control --n 17 --budget 10000 \
  --trial 2500 --decisions 8 --seeds 10,11,12,13 --out runs/agent-control
node app/agent/run.mjs --policy fixed --n 17 --budget 10000 \
  --trial 2500 --decisions 8 --seeds 10,11,12,13 --out runs/agent-fixed
python3 tools/check_agent_reports.py
npm test --prefix app
```

El comprobador revisa las dos evidencias conservadas en `examples/`: huellas del
motor y del orquestador, contabilidad de propuestas, ausencia de inferencia en los
controles y geometría del CSV. El control alternado se repitió y produjo el mismo
informe y CSV byte a byte; los tiempos quedan fuera de esa comparación.

Utilizar una carpeta nueva para cada ejecución: la CLI protege los informes
existentes. El argumento `--budget` limita las propuestas del solver, no tokens
ni tiempo de inferencia. `--decisions` limita cuántas decisiones puede pedir.

## Conectar Gemma local

Una vez instalado Ollama y un modelo Gemma compatible con salida JSON estructurada,
consultar el nombre real del modelo instalado y ejecutar:

```sh
node app/agent/run.mjs --policy ollama --model NOMBRE_INSTALADO \
  --n 17 --budget 10000 --trial 2500 --decisions 8 \
  --seeds 10,11,12,13 --out runs/gemma-first
```

`NOMBRE_INSTALADO` es un marcador que debe sustituirse; no se descarga un modelo
al ejecutar este comando. El adaptador usa por defecto `http://127.0.0.1:11434`.
`--endpoint` admite otro origen HTTP de loopback. Esta versión no acepta un
servicio remoto ni claves de API.

La llamada a `/api/chat` pide una sola respuesta, un esquema JSON, temperatura
cero, semilla 42, hasta 256 tokens de salida y contexto 4.096. El timeout por
petición es 60 segundos. El modelo se descarga de memoria al terminar la petición
(`keep_alive: 0`), lo que puede añadir tiempo de carga a las siguientes decisiones.
No se permite seguir redirecciones; las respuestas tienen un máximo de 64 KiB.

Se registran intentos y respuestas completas de inferencia por separado. Una
conexión fallida no se presenta como un modelo ejecutado. No se guarda texto de
razonamiento interno; la evidencia contiene decisiones de herramientas y medidas.
Temperatura y semilla no garantizan reproducibilidad idéntica de un modelo entre
equipos, cuantizaciones o versiones del servidor.

La API y el esquema siguen la [documentación oficial de Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md).
La [guía de Gemma](https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4)
explica la separación entre proponer una llamada y ejecutarla en la aplicación.
Este adaptador usa decisiones JSON estructuradas; no implementa el protocolo de
tokens de llamadas nativas de Hugging Face ni prueba que todos los modelos Gemma
respondan correctamente a este esquema.

## Qué falta para evaluar IA

1. Elegir y registrar proveedor, modelo, versión y cuantización cuando corresponda.
2. Ejecutar una campaña real y conservar decisiones, errores, consumo y latencia.
3. Comparar contra los controles a igual límite total; registrar si el modelo
   termina antes y cuánto presupuesto utiliza realmente.
4. Repetir en varios tamaños y campañas, separando selección y evaluación.
5. Validar el CSV final y evitar atribuir a la IA las construcciones ya conocidas.

La primera pregunta será si el modelo aporta mejores decisiones que alternar
estrategias con unas pocas líneas de código. Si no las aporta, el experimento
seguirá documentando ese resultado.
