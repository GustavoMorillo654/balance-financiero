"""Cálculo puro de razones financieras para el dashboard y el modelo predictivo."""

from typing import List, Optional

from src.models.balance_sheet import (
    FinancialRatioMetricDTO,
    FinancialRatiosDTO,
    MetricsBaseDTO,
)


class FinancialRatios:
    """Calcula índices financieros sin mutar el balance de entrada.

    Los importes se expresan en la misma moneda del CSV. Las razones se
    devuelven en veces o proporción; los días usan el período configurado.
    Cuando un denominador es cero, el índice queda no disponible y se agrega
    una alerta en vez de producir infinito o NaN.
    """

    DEFAULT_PERIOD_DAYS = 365

    @classmethod
    def _ratio(
        cls,
        numerator: float,
        denominator: float,
        formula: str,
        unidad: str,
        label: str,
        alerts: List[str],
    ) -> FinancialRatioMetricDTO:
        if denominator == 0:
            reason = f"No se puede calcular {label}: el denominador es cero."
            alerts.append(reason)
            return FinancialRatioMetricDTO(
                valor=None,
                formula=formula,
                unidad=unidad,
                disponible=False,
                razon=reason,
            )

        return FinancialRatioMetricDTO(
            valor=numerator / denominator,
            formula=formula,
            unidad=unidad,
        )

    @classmethod
    def _days_from_turnover(
        cls,
        period_days: int,
        turnover: FinancialRatioMetricDTO,
        formula: str,
        label: str,
        alerts: List[str],
    ) -> FinancialRatioMetricDTO:
        if not turnover.disponible or turnover.valor is None:
            reason = f"No se puede calcular {label}: la rotación base no está disponible."
            alerts.append(reason)
            return FinancialRatioMetricDTO(
                valor=None,
                formula=formula,
                unidad="días",
                disponible=False,
                razon=reason,
            )
        if turnover.valor == 0:
            reason = f"No se puede calcular {label}: la rotación base es cero."
            alerts.append(reason)
            return FinancialRatioMetricDTO(
                valor=None,
                formula=formula,
                unidad="días",
                disponible=False,
                razon=reason,
            )
        return FinancialRatioMetricDTO(
            valor=period_days / turnover.valor,
            formula=formula,
            unidad="días",
        )

    @classmethod
    def calculate(
        cls,
        metrics: MetricsBaseDTO,
        periodo_dias: Optional[int] = None,
    ) -> FinancialRatiosDTO:
        """Calcula los cuatro grupos de razones desde las métricas base."""
        alerts: List[str] = []
        configured_period = periodo_dias if periodo_dias is not None else metrics.periodo_dias
        if configured_period <= 0:
            configured_period = cls.DEFAULT_PERIOD_DAYS
            alerts.append(
                f"Período inválido; se utilizó el valor predeterminado de {cls.DEFAULT_PERIOD_DAYS} días."
            )

        razon_corriente = cls._ratio(
            metrics.activo_corriente,
            metrics.pasivo_corriente,
            "activoCorriente / pasivoCorriente",
            "veces",
            "la Razón Corriente",
            alerts,
        )
        prueba_acida = cls._ratio(
            metrics.activo_corriente - metrics.inventario,
            metrics.pasivo_corriente,
            "(activoCorriente - inventario) / pasivoCorriente",
            "veces",
            "la Prueba Ácida",
            alerts,
        )

        deuda_activo = cls._ratio(
            metrics.total_pasivo,
            metrics.total_activo,
            "totalPasivo / totalActivo",
            "proporción",
            "la Razón de Endeudamiento",
            alerts,
        )
        pasivo_patrimonio = cls._ratio(
            metrics.total_pasivo,
            metrics.total_patrimonio,
            "totalPasivo / totalPatrimonio",
            "veces",
            "la Razón Pasivo/Patrimonio",
            alerts,
        )
        autonomia = cls._ratio(
            metrics.total_patrimonio,
            metrics.total_activo,
            "totalPatrimonio / totalActivo",
            "proporción",
            "la Autonomía Financiera",
            alerts,
        )
        apalancamiento_interno = cls._ratio(
            metrics.total_patrimonio,
            metrics.total_pasivo,
            "totalPatrimonio / totalPasivo",
            "veces",
            "la Razón de Apalancamiento Interno",
            alerts,
        )

        rotacion_inventarios = cls._ratio(
            metrics.costos,
            metrics.inventario,
            "costos / inventario",
            "veces",
            "la Rotación de Inventarios",
            alerts,
        )
        rotacion_activos = cls._ratio(
            metrics.ventas,
            metrics.total_activo,
            "ventas / totalActivo",
            "veces",
            "la Rotación de Activos",
            alerts,
        )
        rotacion_cobros = cls._ratio(
            metrics.ventas,
            metrics.cuentas_por_cobrar,
            "ventas / cuentasPorCobrar",
            "veces",
            "la Rotación de Cuentas por Cobrar",
            alerts,
        )

        margen_neto = cls._ratio(
            metrics.utilidad_neta,
            metrics.ventas,
            "utilidadNeta / ventas",
            "proporción",
            "el Margen Neto",
            alerts,
        )
        roa = cls._ratio(
            metrics.utilidad_neta,
            metrics.total_activo,
            "utilidadNeta / totalActivo",
            "proporción",
            "el Rendimiento sobre Activos (ROA)",
            alerts,
        )
        roe = cls._ratio(
            metrics.utilidad_neta,
            metrics.total_patrimonio,
            "utilidadNeta / totalPatrimonio",
            "proporción",
            "el Rendimiento sobre Patrimonio (ROE)",
            alerts,
        )

        return FinancialRatiosDTO(
            periodo_dias=int(configured_period),
            liquidez={
                "razonCorriente": razon_corriente,
                "pruebaAcida": prueba_acida,
                "capitalTrabajo": FinancialRatioMetricDTO(
                    valor=metrics.activo_corriente - metrics.pasivo_corriente,
                    formula="activoCorriente - pasivoCorriente",
                    unidad="moneda",
                ),
            },
            apalancamiento={
                "razonEndeudamiento": deuda_activo,
                "pasivoPatrimonio": pasivo_patrimonio,
                "autonomiaFinanciera": autonomia,
                "apalancamientoInterno": apalancamiento_interno,
            },
            actividad={
                "rotacionInventarios": rotacion_inventarios,
                "diasInventario": cls._days_from_turnover(
                    int(configured_period),
                    rotacion_inventarios,
                    "periodoDias / rotacionInventarios",
                    "los Días de Inventario",
                    alerts,
                ),
                "rotacionActivos": rotacion_activos,
                "rotacionCuentasPorCobrar": rotacion_cobros,
                "periodoCobro": cls._days_from_turnover(
                    int(configured_period),
                    rotacion_cobros,
                    "periodoDias / rotacionCuentasPorCobrar",
                    "el Período de Cobro",
                    alerts,
                ),
            },
            rentabilidad={
                "margenNeto": margen_neto,
                "roa": roa,
                "roe": roe,
            },
            alertas=alerts,
        )
