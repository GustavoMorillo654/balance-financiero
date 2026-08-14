from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AccountCategory(str, Enum):
    """Categorías contables fundamentales."""
    ACTIVO_CORRIENTE = "ACTIVO_CORRIENTE"
    ACTIVO_NO_CORRIENTE = "ACTIVO_NO_CORRIENTE"
    PASIVO_CORRIENTE = "PASIVO_CORRIENTE"
    PASIVO_NO_CORRIENTE = "PASIVO_NO_CORRIENTE"
    PATRIMONIO = "PATRIMONIO"
    INGRESO = "INGRESO"
    EGRESO = "EGRESO"


@dataclass
class Account:
    """Entidad que representa una partida contable individual."""
    id_cuenta: str
    nombre: str
    categoria: AccountCategory
    saldo: float
    vida_util_anios: Optional[float] = None
    depreciable: bool = False
    depreciacion_acumulada: float = 0.0
    valor_neto: float = 0.0

    def __post_init__(self):
        # Si valor_neto no fue inicializado explícitamente, igualarlo a saldo - depreciacion_acumulada
        if self.valor_neto == 0.0 and self.saldo != 0.0 and self.depreciacion_acumulada == 0.0:
            self.valor_neto = self.saldo
