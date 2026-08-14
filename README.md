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

---

## 📁 Estructura del Repositorio

```text
balance-financiero/
├── data/
│   └── dataset_cuentas_ejemplo.csv     # Dataset de prueba balanceado
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account.py                  # Entidad Cuenta y Enum de categorías
│   │   └── balance_sheet.py            # DTOs y serialización del Balance General
│   ├── services/
│   │   ├── __init__.py
│   │   ├── csv_parser.py               # Parser y sanitizador de CSV
│   │   ├── classifier.py               # Clasificador dinámico por liquidez/exigibilidad
│   │   ├── depreciation.py             # Motor de depreciación (con excepción de Terreno)
│   │   └── validator.py                # Validador de ecuación contable y alertas
│   └── index.py                        # Pipeline principal y CLI de la Fase 1
├── tests/
│   ├── test_parser.py                  # Pruebas de lectura y sanitización de CSV
│   ├── test_classifier.py              # Pruebas de categorización semántica
│   ├── test_depreciation.py            # Pruebas de depreciación y regla de Terreno
│   ├── test_validator.py               # Pruebas de validación contable y alertas
│   └── test_pipeline.py                # Pruebas de integración de pipeline completo
├── datos.csv                           # Dataset base proporcionado
├── requirements.txt                    # Dependencias del proyecto
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

### Procesar un archivo CSV con resumen en consola:
```bash
python src/index.py --file data/dataset_cuentas_ejemplo.csv
```

### Exportar el JSON del contrato a un archivo:
```bash
python src/index.py --file data/dataset_cuentas_ejemplo.csv --output balance_salida.json
```

### Imprimir únicamente JSON en la salida estándar:
```bash
python src/index.py --file datos.csv --json
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
