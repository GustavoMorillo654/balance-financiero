#!/usr/bin/env python3
"""
Pipeline Principal de la Fase 1: Estructuración y Modelado del Balance General
Autor: Gustavo Morillo (Persona 1)
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

# Añadir el directorio raíz al path para ejecución directa
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.csv_parser import CSVParser
from src.services.classifier import AccountClassifier
from src.services.credit_evaluation import CreditEvaluation
from src.services.depreciation import DepreciationEngine
from src.services.financial_ratios import FinancialRatios
from src.services.reconciliation import BalanceReconciler
from src.services.validator import AccountingValidator
from src.models.balance_sheet import BalanceSheetResultDTO


def process_balance_content(
    csv_content: str,
    periodo_dias: int = FinancialRatios.DEFAULT_PERIOD_DAYS,
    balance_mode: str = BalanceReconciler.MODE_STRICT,
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de Fase 1 a partir de una cadena con contenido CSV.
    Retorna el diccionario estructurado según el contrato estandarizado.
    """
    # 1. Ingesta y sanitización
    records = CSVParser.parse_content(csv_content)
    if not records:
        return {
            "isValid": False,
            "alerts": ["El archivo CSV no contiene registros contables válidos."],
            "balance": {},
            "metrics_base": {},
            "financial_ratios": {},
            "credit_evaluation": {},
            "balance_adjustment": {},
        }

    # 2. Clasificación dinámica
    accounts = AccountClassifier.classify_records(records)

    # 3. Motor de depreciación (con regla estricta de excepción para Terreno)
    accounts_depreciated, gasto_depreciacion = DepreciationEngine.apply_depreciation(accounts)

    # 4. Validación contable y generación de alertas
    result_dto: BalanceSheetResultDTO = AccountingValidator.build_and_validate(
        accounts=accounts_depreciated,
        depreciacion_periodo=gasto_depreciacion
    )
    result_dto = BalanceReconciler.apply(result_dto, mode=balance_mode)
    result_dto.financial_ratios = FinancialRatios.calculate(
        result_dto.metrics_base,
        periodo_dias=periodo_dias,
    )
    result_dto.metrics_base.periodo_dias = result_dto.financial_ratios.periodo_dias
    result_dto.credit_evaluation = CreditEvaluation.calculate(
        result_dto.financial_ratios,
        balance_is_valid=result_dto.is_valid,
    )

    return result_dto.to_dict()


def process_balance_file(
    filepath: str,
    output_path: Optional[str] = None,
    periodo_dias: int = FinancialRatios.DEFAULT_PERIOD_DAYS,
    balance_mode: str = BalanceReconciler.MODE_STRICT,
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de Fase 1 a partir de la ruta de un archivo CSV.
    Si se especifica output_path, exporta el JSON a dicho archivo.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No se encontró el archivo: {filepath}")

    with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
        content = f.read()

    result = process_balance_content(
        content,
        periodo_dias=periodo_dias,
        balance_mode=balance_mode,
    )

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fase 1: Motor de Balance General Contable (Finanzas para Ingenieros)"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default="datos.csv",
        help="Ruta al archivo CSV con las cuentas contables (por defecto: datos.csv)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Ruta para exportar el JSON estructurado"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprimir únicamente la salida JSON pura"
    )
    parser.add_argument(
        "--period-days",
        type=int,
        default=FinancialRatios.DEFAULT_PERIOD_DAYS,
        help="Días del período para índices de actividad (por defecto: 365)"
    )
    parser.add_argument(
        "--balance-mode",
        choices=(BalanceReconciler.MODE_STRICT, BalanceReconciler.MODE_CONCILIATION),
        default=BalanceReconciler.MODE_STRICT,
        help="strict conserva el descuadre; conciliacion agrega un ajuste temporal en memoria",
    )

    args = parser.parse_args()

    try:
        result = process_balance_file(
            args.file,
            args.output,
            args.period_days,
            args.balance_mode,
        )

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        # Impresión amigable en consola
        print("=" * 70)
        print("  ANÁLISIS FINANCIERO Y EVALUACIÓN DE CRÉDITO (FASES 1–3)")
        print("=" * 70)
        print(f"Archivo procesado: {args.file}")
        print(f"Estado de Balance: {'✅ BALANCEADO' if result['isValid'] else '❌ DESCUADRADO'}")
        
        if result["alerts"]:
            print("\n⚠️ ALERTAS DETECTADAS:")
            for alert in result["alerts"]:
                print(f"  - {alert}")

        adjustment = result.get("balance_adjustment", {})
        if adjustment.get("aplicado"):
            print(
                f"\n⚠️ Ajuste temporal aplicado en memoria: "
                f"${adjustment.get('monto', 0.0):,.2f} al activo."
            )

        bal = result.get("balance", {})
        print("\n--- RESUMEN DE ACTIVOS ---")
        act = bal.get("activo", {})
        print(f"  Activo Corriente:    ${act.get('corriente', {}).get('total', 0.0):,.2f}")
        print(f"  Activo No Corriente: ${act.get('noCorriente', {}).get('total', 0.0):,.2f}")
        print(f"  TOTAL ACTIVO:        ${act.get('totalActivo', 0.0):,.2f}")

        print("\n--- RESUMEN DE PASIVOS ---")
        pas = bal.get("pasivo", {})
        print(f"  Pasivo Corriente:    ${pas.get('corriente', {}).get('total', 0.0):,.2f}")
        print(f"  Pasivo No Corriente: ${pas.get('noCorriente', {}).get('total', 0.0):,.2f}")
        print(f"  TOTAL PASIVO:        ${pas.get('totalPasivo', 0.0):,.2f}")

        print("\n--- RESUMEN DE PATRIMONIO ---")
        pat = bal.get("patrimonio", {})
        print(f"  TOTAL PATRIMONIO:    ${pat.get('total', 0.0):,.2f}")

        print("\n--- MÉTRICAS BASE PARA FASE 2 Y 3 ---")
        mb = result.get("metrics_base", {})
        for k, v in mb.items():
            if k == "periodoDias":
                print(f"  {k}: {v} días")
            elif isinstance(v, (int, float)):
                print(f"  {k}: ${v:,.2f}")
            else:
                print(f"  {k}: {v}")

        print("\n--- DASHBOARD DE ÍNDICES FINANCIEROS ---")
        ratios = result.get("financial_ratios", {})
        for group_name in ("liquidez", "apalancamiento", "actividad", "rentabilidad"):
            print(f"  [{group_name}]")
            for ratio_name, metric in ratios.get(group_name, {}).items():
                value = metric.get("valor")
                rendered = "N/D" if value is None else f"{value:.4f}"
                print(f"    {ratio_name}: {rendered} {metric.get('unidad', '')}".rstrip())
        for alert in ratios.get("alertas", []):
            print(f"  ⚠️ {alert}")

        print("\n--- EVALUACIÓN DISCRIMINANTE DE CRÉDITO ---")
        evaluation = result.get("credit_evaluation", {})
        if evaluation.get("disponible"):
            print(f"  X1 (Razón Corriente): {evaluation['x1']:.4f}")
            print(f"  X2 (Apalancamiento Interno): {evaluation['x2']:.4f}")
            print(f"  Z: {evaluation['zScore']:.4f}")
            print(f"  Dictamen: {evaluation['categoria']}")
        else:
            print("  Dictamen: No evaluable")
        print(f"  {evaluation.get('explicacion', '')}")
        for alert in evaluation.get("alertas", []):
            print(f"  ⚠️ {alert}")
        
        print("\n" + "=" * 70)
        print("JSON Output para Persona 2:")
        print("=" * 70)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error procesando balance: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
