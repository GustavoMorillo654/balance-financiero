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
    """Métricas base requeridas para alimentar Fases 2 y 3."""
    total_activo: float = 0.0
    total_pasivo: float = 0.0
    total_patrimonio: float = 0.0
    activo_corriente: float = 0.0
    pasivo_corriente: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalActivo": round(self.total_activo, 2),
            "totalPasivo": round(self.total_pasivo, 2),
            "totalPatrimonio": round(self.total_patrimonio, 2),
            "activoCorriente": round(self.activo_corriente, 2),
            "pasivoCorriente": round(self.pasivo_corriente, 2),
        }


@dataclass
class BalanceSheetResultDTO:
    """Contrato final de entrega para Persona 2."""
    is_valid: bool = True
    alerts: List[str] = field(default_factory=list)
    balance: BalanceStructureDTO = field(default_factory=BalanceStructureDTO)
    metrics_base: MetricsBaseDTO = field(default_factory=MetricsBaseDTO)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "isValid": self.is_valid,
            "alerts": self.alerts,
            "balance": self.balance.to_dict(),
            "metrics_base": self.metrics_base.to_dict(),
        }
