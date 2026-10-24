# Comprobación de la app — 23-10-2026

## Refactor previo a GitHub — 24-10-2026

Separados el dibujo SVG, análisis compartido, persistencia y tema de cubo. Los
registros locales se validan al leerlos; el solver rechaza entradas y lotes inválidos.
Quince tests web correctos, build estático correcto y referencias contrastadas
contra el CSV exacto evaluado. El texto de los avisos ya describe el contorno
magenta en lugar de atribuir los cruces al color rojo de las piezas.

## Actualización visual — 24-10-2026

Se aplicó una estética de cubo de seis colores sin modificar geometría ni solver.
Comprobados los seis colores en el reto n=10, selección azul, aviso discontinuo de
dos cruces al girar la rejilla n=5, exportación deshabilitada ante cruces y deshacer.
Vista móvil a 390 px sin desbordamiento horizontal. Capturas actualizadas y build
estático regenerado. No se añadieron tests nuevos para este cambio de presentación.

## Automatizada

Diez tests Node correctos: contactos y cruces de 1e-12; valores finitos y dominio;
rotaciones y traslación; filtro espacial frente a SAT exhaustivo; comparación de
referencias con los lados de Python; reparación; rejilla n=1000; exportación CSV;
reproducibilidad y presupuesto; conservación de incumbente fuerte e inicio inválido.

Build estático generado correctamente con Node 24.19.0, sin dependencias.
La CI define Node 22; no se ha ejecutado remotamente.

## Navegador real

Comprobado en el navegador integrado con la app servida por HTTP:

- Giro manual provoca cruces, piezas rojas y exportación deshabilitada.
- Deshacer restaura la configuración; arrastre real y flechas mueven las piezas.
- Referencias n=5/n=10 muestran 2,7071 y 3,9101, sin cruces locales.
- Descarga CSV: n=5, cinco filas completas y cabecera correcta.
- El CSV de esa referencia exportado desde el navegador fue aceptado offline por
  el notebook oficial v17. No acredita aceptación de futuras ediciones ni de las
  nuevas búsquedas del navegador; no se realizó un envío.
- Motor greedy n=5 termina con L≈2,7195 para semilla 42 y presupuesto 2.500;
  annealing por defecto terminó con L≈2,7868 en esta prueba.
- Reto n=1000 representa mil piezas; una búsqueda de 10.000 propuestas pudo
  detenerse y devolvió el control, conservando lado 32.
- Mejor marca local sobrevive a recargar; el tablero vuelve a su rejilla inicial.
- A 390 px, ancho de contenido 375 px con barra de desplazamiento: sin overflow.
- Con los encabezados CSP de Vercel, el worker y la interfaz funcionan y no se
  observaron errores ni advertencias de consola en la prueba final.

Capturas [escritorio](preview.jpg) y [móvil](preview-mobile.jpg). No hay tests E2E
automatizados persistentes: estas comprobaciones de interfaz fueron manuales con
automatización del navegador. No se probó hardware táctil ni el despliegue real
de Vercel. El motor web no ofrece la reanudación exacta del runner Python.
