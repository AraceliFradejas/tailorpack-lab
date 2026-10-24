# Verificación de la entrega M4

Preparada el 23-10-2026. La preparación local incluye una copia descomprimida del
ZIP en otra carpeta y un entorno virtual nuevo, sin instalar dependencias. No se
confunde con una matriz de CI remota ni con un entorno aislado del sistema operativo.

Comandos de comprobación desde la raíz de la copia:

```sh
python -m unittest discover -s tests -v
python -m tailorpack --max-n 16 --seed 42 --out runs/clean-demo
python -m tailorpack.scale --ns 10 1000 --seeds 0 --evaluations 10 \
  --workers 2 --warm-start examples/m2-best/candidate_NOT_VALIDATED.csv --out runs/clean-scale
python -m tailorpack.portfolio
python tools/check_release.py
```

Se comprueban los enlaces locales de documentación, presencia de figuras y la
cadena de validación del candidato final: SHA-256, veinte puzzles aceptados y
1.986 filas. La reproducción completa del evaluador requiere los archivos externos
y dependencias opcionales descritos en `official-validation.md`.

El empaquetador `python3 tools/package_release.py` crea un ZIP de transporte con
orden y fecha interna fijos y un manifiesto SHA-256 de sus archivos. Excluye runs,
descargas, cachés y entornos. El manifiesto no se incluye a sí mismo. Dos paquetes
de fuentes idénticas deben coincidir byte a byte con el mismo entorno de compresión.

Resultado: **32 tests correctos y 5 opcionales omitidos**, demo y escala paralela
hasta n=1000 correctas, mejor semilla n=10 reproducida con L=3.9100797962141782.
El registro completo está en [release-validation.json](release-validation.json).
La galería y el gráfico se revisaron visualmente:
etiquetas completas, escalas comunes por puzzle y sin elementos recortados.
No se ha publicado contenido ni realizado un nuevo envío a Kaggle.
