# Verificación de Kaggle — 23 de octubre de 2026

Primera lectura directa de las páginas públicas en navegador, sin sesión iniciada.
El lector web de texto falló; el navegador sí mostró el contenido. Este documento
resume evidencias, no reproduce las condiciones completas ni sustituye su lectura.

## Fuentes primarias y hechos observados

| Fuente | Hechos confirmados |
|---|---|
| [Overview / Description](https://www.kaggle.com/competitions/squares-in-squares/overview) | Puzzles n=1..1000; n cuadrados unitarios; interiores sin intersección; contenedor cuadrado alineado a ejes; centros continuos y rotaciones en radianes; se permiten puzzles omitidos. |
| [Overview / Evaluation](https://www.kaggle.com/competitions/squares-in-squares/overview/evaluation) | Menor es mejor; suma de L/sqrt(n)-1; id entero único; CSV id,n,square_id,x,y,angle; L se calcula, no se entrega. Literales decimales, incluida notación científica; no expresiones simbólicas. |
| [Data](https://www.kaggle.com/competitions/squares-in-squares/data) | Una fila por cuadrado; id=0..filas-1; square_id=0..n-1; sample_submission.csv, 12,87 MB, seis columnas. El contenido/descarga exige iniciar sesión y aceptar reglas. No se descargó ni se comparó byte a byte. |
| [Metric notebook](https://www.kaggle.com/code/metric/squares-in-squares) | Versión visible 17/17, kernel version 360167936. Cabecera y código inicial: L=max(ancho,alto) de todos los vértices, invariante a traslaciones; puzzles ausentes/inválidos/inviables reciben ceil(sqrt(n))/sqrt(n)-1. Certificación de no solapamiento con mpmath intervalos y escalado 50,100,200,500 dígitos. Medición L a 60 dígitos; submission_details.csv con 50 decimales, cero para puzzles sin L aceptada. |
| [Rules](https://www.kaggle.com/competitions/squares-in-squares/rules) | Equipo máximo 5; máximo 10 envíos diarios y 1 final; una cuenta por persona; no compartir código privadamente entre equipos; compartir públicamente para todos está permitido bajo las condiciones allí descritas. Datos/herramientas externos sujetos a acceso y criterio de razonabilidad; licencia y documentación reproducible exigidas a ganadores, CC BY 4.0 o Apache 2.0 en B(5). |

La página de evaluación renderizó de forma ambigua una raíz en la penalización de
puzzles omitidos. La cabecera del notebook resuelve ese punto explícitamente con
ceil(sqrt(n))/sqrt(n)-1. No se infiere una métrica desde otras competiciones.

## Calendario observado

Inicio 21-10-2026; hitos 17-01-2027 y 18-04-2027; entrada y fusión de equipos
11-07-2027; cierre final 18-07-2027, a las 23:59 UTC salvo cambios del organizador.
Consultar de nuevo antes de participar. Overview dice menor score es mejor y usa
«highest» al describir premios de hito: no interpretamos esa discrepancia como
una inversión de la métrica.

## Actualización M1 (misma fecha)

Posteriormente la sesión del navegador ya tenía acceso a la competición y mostró
Submit Prediction. Se descargaron el sample completo y el notebook v17 sin aceptar
acuerdos ni hacer envíos desde esta tarea. Quedan sustituidas las limitaciones de
descarga y lectura parcial anotadas arriba: se inspeccionó el código completo y
se ejecutó su punto de entrada sin modificaciones sobre rejilla y candidato.
Detalles y hashes en [validación oficial offline](official-validation.md).

## Checklist inicial antes de un envío (M1 ya cubre los primeros cuatro puntos)

- Descargar sample_submission.csv tras entrada autorizada y comparar tipos, orden e índices.
- Obtener y fijar el notebook completo y sus dependencias mediante versión y hash.
- Auditar validaciones de columnas, duplicados, límites, errores globales, contactos
  degenerados y procesos/tiempos: aquí solo se leyó la cabecera y el código inicial,
  no se ejecutó ni auditó íntegramente el evaluador oficial.
- Ejecutar el candidato serializado con ese evaluador y contrastar resultados.
- Revisar cambios de reglas y resolver cualquier ambigüedad con el organizador.

Esta tarea no ha aceptado condiciones, inscrito al usuario ni realizado envíos.
El validador local no demuestra aceptación en Kaggle. No asumimos límites de
hardware, GPU, internet, tolerancias oficiales ni reglas de otras competiciones.
