# Motor Computacional de Análisis Financiero - Fase 1: Balance General

---

## 📌 Descripción del Proyecto

Este proyecto implementa el motor computacional y modular de la **Fase 1**, encargado de procesar datos contables crudos en formato CSV, estructurarlos de forma normalizada según su liquidez y exigibilidad, aplicar depreciaciones en línea recta con reglas de negocio estrictas y validar la ecuación contable fundamental ($\text{Total Activo} = \text{Total Pasivo} + \text{Total Patrimonio}$), entregando un contrato de datos JSON estandarizado para las fases posteriores.

---

## 🚀 Características Principales

1. **Ingesta y Sanitización Tolerante de CSV (`CSVParser`)**:
   - Detección automática de delimitadores (`,`, `;`, `\t`, `|`).
   - Normalización de encabezados con sinónimos/alias en español e inglés.
   - Sanitización robusta de montos numéricos (manejo de `$`, `€`, `Bs.`, `BsF`, formatos `1.500,00` vs `1,500.00` y valores negativos entre paréntesis).
2. **Clasificación Contable Dinámica (`AccountClassifier`)**:
   - Clasificación en: **Activo Corriente**, **Activo No Corriente**, **Pasivo Corriente**, **Pasivo No Corriente**, **Patrimonio**, e **Ingresos / Egresos**.
   - Soporte dual: por columna de tipo/saldo explícita y por catálogo semántico de palabras clave.
   - Cálculo e integración de la **Utilidad Neta del Ejercicio** al Patrimonio cuando se procesan cuentas de resultados.
3. **Motor de Depreciación en Línea Recta (`DepreciationEngine`)**:
   - Cálculo de depreciación anual: $\text{Depreciación} = \frac{\text{Costo Histórico} - \text{Valor Residual}}{\text{Vida Útil}}$.
   - ⚠️ **Regla de Negocio Estricta:** La cuenta **Terreno** es el **único activo fijo que NO se deprecia** (`depreciable: false`, `depreciacionAcumulada: 0.0`, `valorNeto = saldo`).
4. **Validación de la Ecuación Contable (`AccountingValidator`)**:
   - Validación matemática: $\text{Total Activo} = \text{Total Pasivo} + \text{Total Patrimonio}$ con tolerancia $\epsilon = 0.001$.
   - Generación de alertas descriptivas de descuadre y bandera `isValid`.
5. **Contrato de Salida Estandarizado (JSON)**:
   - Formato listo para consumo directo por la Persona 2 (Fases 2 y 3).
6. **Motor de Índices Financieros (`FinancialRatios`)**:
   - Calcula liquidez, apalancamiento, actividad y rentabilidad desde `metrics_base`.
   - Devuelve fórmula, unidad, disponibilidad y alertas para que la CLI o una futura interfaz puedan renderizar un dashboard.
7. **Evaluación Discriminante de Crédito (`CreditEvaluation`)**:
   - Calcula el puntaje `Z` con la Razón Corriente y el Apalancamiento Interno.
   - Emite un dictamen explicable y evita evaluar balances descuadrados o índices no disponibles.
8. **Aplicación web desplegable**:
   - Interfaz estática para cargar CSV, revisar el balance, los índices y el dictamen en una sola vista.
   - API FastAPI lista para Vercel en `POST /api/analyze`.

---

## 📁 Estructura del Repositorio

```text
balance-financiero/
├── api/
│   └── index.py                        # Entrada ASGI para Vercel
├── data/
│   └── dataset_cuentas_ejemplo.csv     # Dataset de prueba balanceado
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account.py                  # Entidad Cuenta y Enum de categorías
│   │   └── balance_sheet.py            # DTOs y serialización del Balance General
│   ├── services/
│   │   ├── __init__.py
│   │   ├── credit_evaluation.py        # Modelo Z y dictamen de crédito
│   │   ├── csv_parser.py               # Parser y sanitizador de CSV
│   │   ├── classifier.py               # Clasificador dinámico por liquidez/exigibilidad
│   │   ├── depreciation.py             # Motor de depreciación (con excepción de Terreno)
│   │   ├── financial_ratios.py         # Índices financieros y alertas de denominadores
│   │   └── validator.py                # Validador de ecuación contable y alertas
│   └── index.py                        # Pipeline principal y CLI de la Fase 1
├── public/
│   └── index.html                      # Interfaz web estática
├── tests/
│   ├── test_parser.py                  # Pruebas de lectura y sanitización de CSV
│   ├── test_classifier.py              # Pruebas de categorización semántica
│   ├── test_credit_evaluation.py       # Pruebas de puntaje Z y umbrales de riesgo
│   ├── test_depreciation.py            # Pruebas de depreciación y regla de Terreno
│   ├── test_financial_ratios.py        # Pruebas de fórmulas y datos insuficientes
│   ├── test_web_api.py                 # Pruebas de interfaz estática y API HTTP
│   ├── test_validator.py               # Pruebas de validación contable y alertas
│   └── test_pipeline.py                # Pruebas de integración de pipeline completo
├── datos.csv                           # Dataset base proporcionado
├── requirements.txt                    # Dependencias del proyecto
├── vercel.json                          # Configuración de función serverless
└── README.md
```

---

## 🛠️ Instalación y Requisitos

Requiere **Python 3.10+**.

```bash
# 1. Crear / activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

## 💻 Uso del Pipeline

### Esquema mínimo de entrada CSV

El archivo debe incluir una fila de encabezados y, como mínimo, las columnas `id_cuenta`, `descripcion_cuenta` y `monto`. `tipo_saldo` y `vida_util_anios` son opcionales: el tipo puede inferirse por el nombre de la cuenta y la vida útil solo aplica a activos depreciables. El parser también acepta los alias documentados en `CSVParser.COLUMN_ALIASES`, delimitadores `,`, `;`, tabulador o `|`, y montos con formatos monetarios latinoamericanos o anglosajones.

Ejemplo canónico:

```csv
id_cuenta,descripcion_cuenta,tipo_saldo,monto,vida_util_anios
1,Caja y Bancos,liquidez,15000,
2,Maquinaria,inversion,30000,10
3,Capital Social,patrimonio,60000,
```

### Procesar un archivo CSV con resumen en consola:
```bash
python src/index.py --file data/dataset_cuentas_ejemplo.csv
```

### Ejecutar la aplicación web localmente

```bash
.venv/bin/uvicorn src.web:app --reload
```

Abra `http://127.0.0.1:8000`. La interfaz envía el archivo a `POST /api/analyze` como `multipart/form-data`; admite el campo `file` y el parámetro opcional `period_days` (1–366). El archivo debe ser `.csv` y no superar 5 MB. `GET /api/health` permite comprobar el estado de la función.

### Desplegar en Vercel

El repositorio incluye `api/index.py`, `public/` y `vercel.json`, por lo que no requiere variables de entorno ni almacenamiento persistente. Después de iniciar sesión y vincular el proyecto, despliegue con:

```bash
npx vercel link --yes
npx vercel --prod --yes
```

Vercel sirve `public/index.html` y ejecuta la aplicación FastAPI como función Python. Consulte `docs/ARCHITECTURE.md` para el flujo técnico y `docs/DEFENSA.md` para la demostración.

La versión de producción disponible es [balance-financiero-delta.vercel.app](https://balance-financiero-delta.vercel.app).

### Exportar el JSON del contrato a un archivo:
```bash
python src/index.py --file data/dataset_cuentas_ejemplo.csv --output balance_salida.json
```

### Imprimir únicamente JSON en la salida estándar:
```bash
python src/index.py --file datos.csv --json
```

El período de actividad se puede configurar en días (365 por defecto):

```bash
python src/index.py --file datos.csv --period-days 360
```

---

## 🧪 Ejecución de Pruebas Unitarias

Para ejecutar toda la suite de pruebas unitarias e integrales con `pytest`:

```bash
pytest tests/ -v
```

---

## 🤝 Contrato de Datos para Persona 2 (Fases 2 y 3)

El objeto JSON retornado por la Fase 1 posee la siguiente estructura:

```json
{
  "isValid": true,
  "alerts": [],
  "balance": {
    "activo": {
      "corriente": {
        "cuentas": [
          { "nombre": "Caja y Bancos", "saldo": 15000.0 }
        ],
        "total": 15000.0
      },
      "noCorriente": {
        "cuentas": [
          { "nombre": "Terreno", "saldo": 50000.0, "depreciable": false, "depreciacionAcumulada": 0.0, "valorNeto": 50000.0 },
          { "nombre": "Maquinaria", "saldo": 30000.0, "depreciable": true, "depreciacionAcumulada": 3000.0, "valorNeto": 27000.0 }
        ],
        "total": 77000.0
      },
      "totalActivo": 92000.0
    },
    "pasivo": {
      "corriente": {
        "cuentas": [
          { "nombre": "Proveedores", "saldo": 12000.0 }
        ],
        "total": 12000.0
      },
      "noCorriente": {
        "cuentas": [
          { "nombre": "Préstamos Bancarios LP", "saldo": 20000.0 }
        ],
        "total": 20000.0
      },
      "totalPasivo": 32000.0
    },
    "patrimonio": {
      "cuentas": [
        { "nombre": "Capital Social", "saldo": 60000.0 }
      ],
      "total": 60000.0
    }
  },
  "metrics_base": {
    "totalActivo": 92000.0,
    "totalPasivo": 32000.0,
    "totalPatrimonio": 60000.0,
    "activoCorriente": 15000.0,
    "pasivoCorriente": 12000.0
  }
}
```

Este contrato base es la fuente única para la CLI y las futuras API y vistas. Las fases posteriores deben conservar `isValid`, `alerts`, `balance` y `metrics_base`, y añadir sus resultados en propiedades nuevas sin cambiar los nombres existentes.

### Índices financieros (Fase 2)

El pipeline añade `financial_ratios` con cuatro grupos. Todas las razones se calculan con los importes del mismo período; los índices de proporción se expresan como decimal (por ejemplo, `0.35` equivale a 35%). Si un denominador es cero, el campo devuelve `valor: null`, `disponible: false` y una explicación en `razon` y `alertas`; nunca se generan `Infinity` o `NaN`.

| Grupo | Índices | Fórmula |
|---|---|---|
| Liquidez | Razón Corriente, Prueba Ácida, Capital de Trabajo | `AC / PC`, `(AC - Inventario) / PC`, `AC - PC` |
| Apalancamiento | Endeudamiento, Pasivo/Patrimonio, Autonomía, Apalancamiento Interno | `Pasivo / Activo`, `Pasivo / Patrimonio`, `Patrimonio / Activo`, `Patrimonio / Pasivo` |
| Actividad | Rotación de Inventarios, Activos y Cobros | `Costos / Inventario`, `Ventas / Activo`, `Ventas / CxC` |
| Rentabilidad | Margen Neto, ROA, ROE | `Utilidad Neta / Ventas`, `/ Activo`, `/ Patrimonio` |

El campo `metrics_base` ahora incluye `inventario`, `cuentasPorCobrar`, `ventas`, `costos`, `egresos`, `utilidadNeta`, `depreciacionPeriodo` y `periodoDias`, además de los totales originales.

### Evaluación de crédito (Fase 3)

El contrato añade `credit_evaluation` con `x1`, `x2`, `zScore`, `categoria`, `explicacion`, `disponible` y `alertas`. El modelo usa:

```text
X1 = activoCorriente / pasivoCorriente
X2 = totalPatrimonio / totalPasivo
Z = 0.4 * X1 + 0.6 * X2
```

`X2` es la Razón de Apalancamiento Interno: aportes de propietarios por cada unidad monetaria tomada de terceros, según la formulación documentada en esta [referencia académica](https://www.dspace.cordillera.edu.ec/bitstream/123456789/5360/1/74-EMP-FIN-15-15-1719278184.pdf).

| Puntaje Z | Dictamen |
|---|---|
| `Z > 1.4` | Crédito excelente |
| `0.66 ≤ Z ≤ 1.4` | Crédito de riesgo normal |
| `Z < 0.66` | Crédito malo |

El dictamen es `No evaluable` si el balance está descuadrado, si `X1` o `X2` no se puede calcular, o si algún denominador requerido es cero. La CLI imprime el puntaje y su explicación después del dashboard de índices.
