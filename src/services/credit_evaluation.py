"""Modelo discriminante para emitir un dictamen automatizado de crédito."""

from src.models.balance_sheet import CreditEvaluationDTO, FinancialRatioMetricDTO, FinancialRatiosDTO


class CreditEvaluation:
    """Calcula Z = 0.4 * X1 + 0.6 * X2 a partir de los índices financieros."""

    EXCELLENT_THRESHOLD = 1.4
    NORMAL_THRESHOLD = 0.66

    @staticmethod
    def _unavailable_metric(
        metric: FinancialRatioMetricDTO | None,
        metric_name: str,
    ) -> str:
        if metric is None:
            return f"No se puede calcular {metric_name}: el índice financiero no está disponible."
        if metric.razon:
            return f"No se puede calcular {metric_name}: {metric.razon}"
        return f"No se puede calcular {metric_name}: el índice financiero no está disponible."

    @classmethod
    def calculate(
        cls,
        ratios: FinancialRatiosDTO,
        balance_is_valid: bool = True,
    ) -> CreditEvaluationDTO:
        """Devuelve el puntaje Z y su categoría, o alertas si la entrada no es válida.

        X1 reutiliza la Razón Corriente de Fase 2. X2 reutiliza el
        Apalancamiento Interno: Total Patrimonio / Total Pasivo.
        """
        if not balance_is_valid:
            alert = "No se puede emitir el dictamen: el balance contable presenta un descuadre."
            return CreditEvaluationDTO(
                explicacion=alert,
                alertas=[alert],
            )

        x1_metric = ratios.liquidez.get("razonCorriente")
        x2_metric = ratios.apalancamiento.get("apalancamientoInterno")
        alerts = []

        if x1_metric is None or not x1_metric.disponible or x1_metric.valor is None:
            alerts.append(cls._unavailable_metric(x1_metric, "X1 (Razón Corriente)"))
        if x2_metric is None or not x2_metric.disponible or x2_metric.valor is None:
            alerts.append(cls._unavailable_metric(x2_metric, "X2 (Apalancamiento Interno)"))

        if alerts:
            return CreditEvaluationDTO(
                explicacion="No se puede emitir el dictamen porque faltan índices requeridos.",
                alertas=alerts,
            )

        x1 = x1_metric.valor
        x2 = x2_metric.valor
        z_score = 0.4 * x1 + 0.6 * x2

        if z_score > cls.EXCELLENT_THRESHOLD:
            categoria = "Crédito excelente"
            explanation = f"Z = {z_score:.4f} es mayor que {cls.EXCELLENT_THRESHOLD}."
        elif z_score >= cls.NORMAL_THRESHOLD:
            categoria = "Crédito de riesgo normal"
            explanation = (
                f"Z = {z_score:.4f} está entre {cls.NORMAL_THRESHOLD} y "
                f"{cls.EXCELLENT_THRESHOLD}, inclusive."
            )
        else:
            categoria = "Crédito malo"
            explanation = f"Z = {z_score:.4f} es menor que {cls.NORMAL_THRESHOLD}."

        return CreditEvaluationDTO(
            x1=x1,
            x2=x2,
            z_score=z_score,
            categoria=categoria,
            explicacion=explanation,
            disponible=True,
        )
