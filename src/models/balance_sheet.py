from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AccountDTO:
    """DTO para una cuenta dentro del Balance General."""
    nombre: str
    saldo: float
    id_cuenta: Optional[str] = None
    depreciable: Optional[bool] = None
    depreciacion_acumulada: Optional[float] = None
    valor_neto: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "nombre": self.nombre,
            "saldo": round(self.saldo, 2),
        }
        if self.depreciable is not None:
            data["depreciable"] = self.depreciable
            data["depreciacionAcumulada"] = round(self.depreciacion_acumulada or 0.0, 2)
            data["valorNeto"] = round(self.valor_neto if self.valor_neto is not None else self.saldo, 2)
        return data


@dataclass
class SubCategoryDTO:
    """DTO para subcategoría (ej. Corriente o No Corriente)."""
    cuentas: List[AccountDTO] = field(default_factory=list)
    total: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cuentas": [c.to_dict() for c in self.cuentas],
            "total": round(self.total, 2),
        }


@dataclass
class ActivoSectionDTO:
    """DTO para la sección de Activos."""
    corriente: SubCategoryDTO = field(default_factory=SubCategoryDTO)
    no_corriente: SubCategoryDTO = field(default_factory=SubCategoryDTO)
    total_activo: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "corriente": self.corriente.to_dict(),
            "noCorriente": self.no_corriente.to_dict(),
            "totalActivo": round(self.total_activo, 2),
        }


@dataclass
class PasivoSectionDTO:
    """DTO para la sección de Pasivos."""
    corriente: SubCategoryDTO = field(default_factory=SubCategoryDTO)
    no_corriente: SubCategoryDTO = field(default_factory=SubCategoryDTO)
    total_pasivo: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "corriente": self.corriente.to_dict(),
            "noCorriente": self.no_corriente.to_dict(),
            "totalPasivo": round(self.total_pasivo, 2),
        }


@dataclass
class PatrimonioSectionDTO:
    """DTO para la sección de Patrimonio."""
    cuentas: List[AccountDTO] = field(default_factory=list)
    total: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cuentas": [c.to_dict() for c in self.cuentas],
            "total": round(self.total, 2),
        }


@dataclass
class BalanceStructureDTO:
    """Estructura interna del balance (Activo, Pasivo, Patrimonio)."""
    activo: ActivoSectionDTO = field(default_factory=ActivoSectionDTO)
    pasivo: PasivoSectionDTO = field(default_factory=PasivoSectionDTO)
    patrimonio: PatrimonioSectionDTO = field(default_factory=PatrimonioSectionDTO)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activo": self.activo.to_dict(),
            "pasivo": self.pasivo.to_dict(),
            "patrimonio": self.patrimonio.to_dict(),
        }


@dataclass
class MetricsBaseDTO:
    """Métricas base del balance y datos operativos para las Fases 2 y 3."""
    total_activo: float = 0.0
    total_pasivo: float = 0.0
    total_patrimonio: float = 0.0
    activo_corriente: float = 0.0
    pasivo_corriente: float = 0.0
    inventario: float = 0.0
    cuentas_por_cobrar: float = 0.0
    ventas: float = 0.0
    costos: float = 0.0
    egresos: float = 0.0
    utilidad_neta: float = 0.0
    depreciacion_periodo: float = 0.0
    periodo_dias: int = 365

    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalActivo": round(self.total_activo, 2),
            "totalPasivo": round(self.total_pasivo, 2),
            "totalPatrimonio": round(self.total_patrimonio, 2),
            "activoCorriente": round(self.activo_corriente, 2),
            "pasivoCorriente": round(self.pasivo_corriente, 2),
            "inventario": round(self.inventario, 2),
            "cuentasPorCobrar": round(self.cuentas_por_cobrar, 2),
            "ventas": round(self.ventas, 2),
            "costos": round(self.costos, 2),
            "egresos": round(self.egresos, 2),
            "utilidadNeta": round(self.utilidad_neta, 2),
            "depreciacionPeriodo": round(self.depreciacion_periodo, 2),
            "periodoDias": self.periodo_dias,
        }


@dataclass
class FinancialRatioMetricDTO:
    """Resultado de un índice con fórmula y disponibilidad para el dashboard."""
    valor: Optional[float]
    formula: str
    unidad: str
    disponible: bool = True
    razon: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valor": round(self.valor, 4) if self.valor is not None else None,
            "formula": self.formula,
            "unidad": self.unidad,
            "disponible": self.disponible,
            "razon": self.razon,
        }


@dataclass
class FinancialRatiosDTO:
    """Panel estructurado de razones financieras calculadas para un período."""
    periodo_dias: int = 365
    liquidez: Dict[str, FinancialRatioMetricDTO] = field(default_factory=dict)
    apalancamiento: Dict[str, FinancialRatioMetricDTO] = field(default_factory=dict)
    actividad: Dict[str, FinancialRatioMetricDTO] = field(default_factory=dict)
    rentabilidad: Dict[str, FinancialRatioMetricDTO] = field(default_factory=dict)
    alertas: List[str] = field(default_factory=list)

    @staticmethod
    def _serialize_group(group: Dict[str, FinancialRatioMetricDTO]) -> Dict[str, Any]:
        return {name: metric.to_dict() for name, metric in group.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "periodoDias": self.periodo_dias,
            "liquidez": self._serialize_group(self.liquidez),
            "apalancamiento": self._serialize_group(self.apalancamiento),
            "actividad": self._serialize_group(self.actividad),
            "rentabilidad": self._serialize_group(self.rentabilidad),
            "alertas": self.alertas,
        }


@dataclass
class CreditEvaluationDTO:
    """Resultado del modelo discriminante de evaluación de crédito."""
    x1: Optional[float] = None
    x2: Optional[float] = None
    z_score: Optional[float] = None
    categoria: str = "No evaluable"
    explicacion: str = "La evaluación aún no ha sido calculada."
    disponible: bool = False
    alertas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formula": "Z = 0.4 * X1 + 0.6 * X2",
            "x1": round(self.x1, 4) if self.x1 is not None else None,
            "x2": round(self.x2, 4) if self.x2 is not None else None,
            "zScore": round(self.z_score, 4) if self.z_score is not None else None,
            "categoria": self.categoria,
            "explicacion": self.explicacion,
            "disponible": self.disponible,
            "alertas": self.alertas,
        }


@dataclass
class BalanceSheetResultDTO:
    """Contrato final de entrega para Persona 2."""
    is_valid: bool = True
    alerts: List[str] = field(default_factory=list)
    balance: BalanceStructureDTO = field(default_factory=BalanceStructureDTO)
    metrics_base: MetricsBaseDTO = field(default_factory=MetricsBaseDTO)
    financial_ratios: FinancialRatiosDTO = field(default_factory=FinancialRatiosDTO)
    credit_evaluation: CreditEvaluationDTO = field(default_factory=CreditEvaluationDTO)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "isValid": self.is_valid,
            "alerts": self.alerts,
            "balance": self.balance.to_dict(),
            "metrics_base": self.metrics_base.to_dict(),
            "financial_ratios": self.financial_ratios.to_dict(),
            "credit_evaluation": self.credit_evaluation.to_dict(),
        }
