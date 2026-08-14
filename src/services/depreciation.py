import unicodedata
from typing import List, Optional, Tuple
from src.models.account import Account, AccountCategory


class DepreciationEngine:
    """Motor de cálculo de depreciación en línea recta con regla estricta para Terreno."""

    @staticmethod
    def is_terreno(account_name: str) -> bool:
        """Determina con certeza estricta si la cuenta representa un Terreno."""
        nfd = unicodedata.normalize("NFD", account_name)
        clean_name = "".join(c for c in nfd if unicodedata.category(c) != "Mn").lower().strip()
        # Verificar coincidencia exacta de palabra o subcadena clave
        return "terreno" in clean_name or "tierras" in clean_name or "lote" in clean_name

    @classmethod
    def calculate_straight_line(
        cls,
        costo_historico: float,
        vida_util_anios: Optional[float],
        valor_residual: float = 0.0,
        periodos_transcurridos: float = 1.0
    ) -> Tuple[float, float]:
        """
        Calcula la depreciación acumulada y el valor neto usando el método de línea recta:
        Depreciación Período = (Costo Histórico - Valor Residual) / Vida Útil
        Retorna (depreciacion_acumulada, valor_neto).
        """
        if vida_util_anios is None or vida_util_anios <= 0:
            return 0.0, costo_historico

        depreciacion_anual = max(0.0, (costo_historico - valor_residual) / vida_util_anios)
        depreciacion_acumulada = min(costo_historico, round(depreciacion_anual * periodos_transcurridos, 2))
        valor_neto = round(costo_historico - depreciacion_acumulada, 2)
        return depreciacion_acumulada, valor_neto

    @classmethod
    def apply_depreciation(cls, accounts: List[Account]) -> Tuple[List[Account], float]:
        """
        Aplica depreciación a todos los activos fijos de la lista de cuentas.
        Garantiza que la cuenta Terreno nunca sea depreciada.
        Retorna (lista_cuentas_actualizadas, total_gasto_depreciacion_periodo).
        """
        total_depreciacion_periodo = 0.0

        for account in accounts:
            if account.categoria == AccountCategory.ACTIVO_NO_CORRIENTE:
                # Regla de negocio estricta: Terreno es el ÚNICO activo fijo que NO se deprecia
                if cls.is_terreno(account.nombre):
                    account.depreciable = False
                    account.depreciacion_acumulada = 0.0
                    account.valor_neto = round(account.saldo, 2)
                else:
                    # Activo no corriente sujeto a depreciación
                    if account.vida_util_anios and account.vida_util_anios > 0:
                        account.depreciable = True
                        dep_acum, v_neto = cls.calculate_straight_line(
                            costo_historico=account.saldo,
                            vida_util_anios=account.vida_util_anios,
                            valor_residual=0.0,
                            periodos_transcurridos=1.0
                        )
                        account.depreciacion_acumulada = dep_acum
                        account.valor_neto = v_neto
                        total_depreciacion_periodo += dep_acum
                    else:
                        # Sin vida útil especificada
                        account.depreciable = False
                        account.depreciacion_acumulada = 0.0
                        account.valor_neto = round(account.saldo, 2)
            else:
                # Para cualquier otra categoría no aplica depreciación
                account.depreciable = False
                account.depreciacion_acumulada = 0.0
                account.valor_neto = round(account.saldo, 2)

        return accounts, round(total_depreciacion_periodo, 2)
