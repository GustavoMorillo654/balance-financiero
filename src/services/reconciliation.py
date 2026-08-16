"""Conciliación explícita y temporal de balances descuadrados."""

from src.models.balance_sheet import (
    AccountDTO,
    BalanceAdjustmentDTO,
    BalanceSheetResultDTO,
)


class BalanceReconciler:
    """Aplica un ajuste en memoria sin modificar el CSV original."""

    MODE_STRICT = "strict"
    MODE_CONCILIATION = "conciliacion"

    @classmethod
    def apply(
        cls,
        result: BalanceSheetResultDTO,
        mode: str = MODE_STRICT,
    ) -> BalanceSheetResultDTO:
        if mode != cls.MODE_CONCILIATION or result.is_valid:
            return result

        metrics = result.metrics_base
        difference = metrics.total_pasivo + metrics.total_patrimonio - metrics.total_activo
        if difference == 0:
            return result

        adjustment_account = AccountDTO(
            nombre="Ajuste de Conciliación (temporal)",
            saldo=difference,
            id_cuenta="AJUSTE_CONCILIACION",
            ajuste_temporal=True,
        )
        result.balance.activo.corriente.cuentas.append(adjustment_account)
        result.balance.activo.corriente.total += difference
        result.balance.activo.total_activo += difference

        metrics.activo_corriente += difference
        metrics.total_activo += difference

        result.balance_adjustment = BalanceAdjustmentDTO(
            aplicado=True,
            monto=difference,
            lado="activo",
            diferencia_original=-difference,
            descripcion=(
                "Se añadió únicamente en memoria una cuenta puente al activo "
                "para permitir el análisis. El archivo CSV permanece intacto."
            ),
        )
        result.alerts.append(
            f"Advertencia: se aplicó un ajuste temporal de {round(difference, 2)} "
            "al activo; revise el CSV original antes de tomar decisiones."
        )
        result.is_valid = True
        return result

