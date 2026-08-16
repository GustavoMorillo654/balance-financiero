# Plan de Implementación — Balance Financiero

## Objetivo

Construir un sistema que reciba cuentas contables en CSV, produzca un balance general validado, calcule razones financieras y emita una clasificación de riesgo mediante análisis discriminante. La salida debe poder consumirse tanto desde la CLI como desde una aplicación web.

## Estado actual del repositorio

- `src/services/` ya contiene parser CSV, clasificador, depreciación y validador.
- `src/models/` define `Account` y el contrato DTO del balance.
- `src/index.py` expone el pipeline por CLI (`--file`, `--json`, `--output`).
- `tests/` cubre parser, clasificación, depreciación, validación y pipeline.
- No existe todavía motor de índices, modelo predictivo, frontend, API HTTP ni configuración de Vercel.

## Fase 0 — Preparación y contrato

- [x] Confirmar Python 3.10+ y crear `.venv`.
- [x] Instalar `requirements.txt` y ejecutar `pytest tests/ -v` como línea base (18 pruebas pasan).
- [x] Documentar el esquema mínimo del CSV: identificador, nombre, tipo opcional, saldo y vida útil opcional.
- [x] Definir el contrato JSON único para CLI, API, dashboard y predicción, manteniendo las claves existentes (`isValid`, `balance`, `metrics_base`).

## Fase 1 — Balance general (implementado; verificar)

- [x] Leer CSV con delimitadores y alias de columnas tolerantes.
- [x] Normalizar importes, valores negativos y vida útil.
- [x] Clasificar activo corriente/no corriente, pasivo corriente/no corriente, patrimonio e ingresos/egresos.
- [x] Aplicar línea recta y garantizar que `Terreno` no se deprecie.
- [x] Construir el DTO JSON y validar `Activo = Pasivo + Patrimonio` con alertas.
- [x] Cubrir reglas principales con pruebas unitarias e integración.
- [x] Ejecutar la suite en un entorno con pytest instalado y registrar el resultado (28 pruebas pasan en la última ejecución).

## Fase 2 — Índices financieros y dashboard

- [x] Definir fórmulas, período configurable (365 días por defecto), unidades y comportamiento ante divisiones entre cero.
- [x] Ampliar `metrics_base` con inventario, cuentas por cobrar, ventas, costos, egresos, utilidad neta, depreciación y período.
- [x] Implementar el servicio puro `FinancialRatios` y añadir sus resultados al contrato (`financial_ratios`).
- [x] Añadir pruebas de fórmulas, redondeo, datos ausentes, período inválido y alertas de denominador cero.
- [x] Crear un dashboard textual en la CLI con los cuatro grupos, fórmula, valor, unidad y alertas; la vista web queda para la Fase 4.
- [x] Verificar que distintas cargas de CSV recalculan el balance y el dashboard sin reiniciar la aplicación.

## Fase 3 — Predicción discriminante

- [x] Confirmar y documentar `X2 = totalPatrimonio / totalPasivo` como Razón de Apalancamiento Interno.
- [x] Calcular `X1 = Razón Corriente` y `Z = 0.4·X1 + 0.6·X2` reutilizando los índices de la Fase 2.
- [x] Implementar umbrales: `Z > 1.4` crédito excelente; `0.66 ≤ Z ≤ 1.4` riesgo normal; `Z < 0.66` crédito malo.
- [x] Exponer `x1`, `x2`, `zScore`, categoría, explicación, disponibilidad y alertas en `credit_evaluation`.
- [x] Probar ambos límites (`0.66`, `1.4`), crédito excelente/malo, balance descuadrado y denominador cero.

## Fase 4 — Aplicación web, despliegue y defensa

- [x] Elegir y documentar arquitectura web compatible con el pipeline Python (FastAPI + cliente estático + función Vercel).
- [x] Implementar carga de CSV, validación de errores, progreso y presentación de balance, índices y dictamen.
- [x] Añadir pruebas de API y smoke tests de carga para `data/dataset_cuentas_ejemplo.csv` y `datos.csv`.
- [ ] Conectar automáticamente el repositorio GitHub a Vercel; el despliegue directo está activo, pero la vinculación requiere permisos de escritura/administración en `GustavoMorillo654/balance-financiero`.
- [x] Verificar en la URL pública cargas de CSV, recálculo completo y respuesta de predicción o `No evaluable` cuando el balance está descuadrado.
- [x] Añadir modo opcional de conciliación temporal en memoria para CSV descuadrados, manteniendo `strict` y el archivo original intactos.
- [x] Preparar una guía de defensa: arquitectura, flujo CSV→DTO→índices→Z, interpretación y limitaciones.

## Criterio de finalización

- [x] Un CSV válido produce el contrato completo y reproducible desde CLI y web.
- [x] Un CSV inválido muestra errores accionables sin romper la interfaz.
- [x] La suite automatizada pasa y el despliegue público supera el smoke test de extremo a extremo.
