# Guía de defensa

## Demostración en vivo

1. Abra la URL desplegada y cargue el CSV entregado durante la evaluación.
2. Explique que el navegador envía el archivo a `POST /api/analyze`.
3. Seleccione `Conciliación temporal` para `datos.csv`; muestre el balance clasificado y explique que el ajuste de 30.000 se crea solo en memoria. Confirme que `Activo = Pasivo + Patrimonio` después del ajuste.
4. Revise las tarjetas de liquidez, apalancamiento, actividad y rentabilidad; las métricas sin datos se muestran como `N/D` con una alerta.
5. Explique el dictamen: `X1 = Activo Corriente / Pasivo Corriente`, `X2 = Patrimonio / Pasivo` y `Z = 0.4 × X1 + 0.6 × X2`.
6. Relacione el puntaje con la categoría de crédito y cite cualquier alerta o descuadre antes de dar una recomendación.

## Límites que se deben comunicar

- El dictamen es una ayuda académica; no sustituye una evaluación profesional de crédito.
- En modo estricto, un balance descuadrado o un denominador cero produce `No evaluable`, no una recomendación inventada. La conciliación temporal no reemplaza la corrección del CSV.
- Los resultados dependen de la clasificación y exactitud de las cuentas contenidas en el CSV.

## Comprobación antes de la sesión

- Ejecute `.venv/bin/pytest tests/ -q`.
- Pruebe la carga de `data/dataset_cuentas_ejemplo.csv` y `datos.csv`.
- Confirme la URL de producción y una conexión estable.
