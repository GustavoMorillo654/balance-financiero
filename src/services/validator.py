import math
from typing import List, Tuple
from src.models.account import Account, AccountCategory
from src.models.balance_sheet import (
    AccountDTO,
    SubCategoryDTO,
    ActivoSectionDTO,
    PasivoSectionDTO,
    PatrimonioSectionDTO,
    BalanceStructureDTO,
    MetricsBaseDTO,
    BalanceSheetResultDTO,
)


class AccountingValidator:
    """Validador de la ecuación contable fundamental y ensamblador del DTO estandarizado."""

    DEFAULT_TOLERANCE = 0.001

    @classmethod
    def build_and_validate(
        cls,
        accounts: List[Account],
        depreciacion_periodo: float = 0.0,
        tolerance: float = DEFAULT_TOLERANCE
    ) -> BalanceSheetResultDTO:
        """
        Estructura las cuentas en sus secciones correspondientes, calcula subtotales y totales,
        valida la ecuación Activo = Pasivo + Patrimonio y retorna el DTO del contrato.
        """
        activo_corriente_dtos: List[AccountDTO] = []
        activo_no_corriente_dtos: List[AccountDTO] = []
        pasivo_corriente_dtos: List[AccountDTO] = []
        pasivo_no_corriente_dtos: List[AccountDTO] = []
        patrimonio_dtos: List[AccountDTO] = []

        total_ingresos = 0.0
        total_egresos = 0.0
        has_results_accounts = False

        for acc in accounts:
            if acc.categoria == AccountCategory.ACTIVO_CORRIENTE:
                activo_corriente_dtos.append(
                    AccountDTO(nombre=acc.nombre, saldo=acc.saldo, id_cuenta=acc.id_cuenta)
                )
            elif acc.categoria == AccountCategory.ACTIVO_NO_CORRIENTE:
                activo_no_corriente_dtos.append(
                    AccountDTO(
                        nombre=acc.nombre,
                        saldo=acc.saldo,
                        id_cuenta=acc.id_cuenta,
                        depreciable=acc.depreciable,
                        depreciacion_acumulada=acc.depreciacion_acumulada,
                        valor_neto=acc.valor_neto,
                    )
                )
            elif acc.categoria == AccountCategory.PASIVO_CORRIENTE:
                pasivo_corriente_dtos.append(
                    AccountDTO(nombre=acc.nombre, saldo=acc.saldo, id_cuenta=acc.id_cuenta)
                )
            elif acc.categoria == AccountCategory.PASIVO_NO_CORRIENTE:
                pasivo_no_corriente_dtos.append(
                    AccountDTO(nombre=acc.nombre, saldo=acc.saldo, id_cuenta=acc.id_cuenta)
                )
            elif acc.categoria == AccountCategory.PATRIMONIO:
                patrimonio_dtos.append(
                    AccountDTO(nombre=acc.nombre, saldo=acc.saldo, id_cuenta=acc.id_cuenta)
                )
            elif acc.categoria == AccountCategory.INGRESO:
                total_ingresos += acc.saldo
                has_results_accounts = True
            elif acc.categoria == AccountCategory.EGRESO:
                total_egresos += acc.saldo
                has_results_accounts = True

        # Si existen cuentas de ingresos y egresos, calcular Utilidad del Ejercicio
        if has_results_accounts:
            utilidad_ejercicio = total_ingresos - total_egresos - depreciacion_periodo
            patrimonio_dtos.append(
                AccountDTO(
                    nombre="Utilidad Neta del Ejercicio",
                    saldo=round(utilidad_ejercicio, 2),
                    id_cuenta="RES_NETO"
                )
            )

        # Cálculo de totales por subcategoría y sección
        total_act_corr = sum(c.saldo for c in activo_corriente_dtos)
        # El total de activo no corriente se suma a partir de los valores netos
        total_act_no_corr = sum(
            (c.valor_neto if c.valor_neto is not None else c.saldo)
            for c in activo_no_corriente_dtos
        )
        total_activo = total_act_corr + total_act_no_corr

        total_pas_corr = sum(c.saldo for c in pasivo_corriente_dtos)
        total_pas_no_corr = sum(c.saldo for c in pasivo_no_corriente_dtos)
        total_pasivo = total_pas_corr + total_pas_no_corr

        total_patrimonio = sum(c.saldo for c in patrimonio_dtos)

        # Construcción de DTOs jerárquicos
        activo_section = ActivoSectionDTO(
            corriente=SubCategoryDTO(cuentas=activo_corriente_dtos, total=round(total_act_corr, 2)),
            no_corriente=SubCategoryDTO(cuentas=activo_no_corriente_dtos, total=round(total_act_no_corr, 2)),
            total_activo=round(total_activo, 2)
        )

        pasivo_section = PasivoSectionDTO(
            corriente=SubCategoryDTO(cuentas=pasivo_corriente_dtos, total=round(total_pas_corr, 2)),
            no_corriente=SubCategoryDTO(cuentas=pasivo_no_corriente_dtos, total=round(total_pas_no_corr, 2)),
            total_pasivo=round(total_pasivo, 2)
        )

        patrimonio_section = PatrimonioSectionDTO(
            cuentas=patrimonio_dtos,
            total=round(total_patrimonio, 2)
        )

        balance_struct = BalanceStructureDTO(
            activo=activo_section,
            pasivo=pasivo_section,
            patrimonio=patrimonio_section
        )

        metrics_base = MetricsBaseDTO(
            total_activo=round(total_activo, 2),
            total_pasivo=round(total_pasivo, 2),
            total_patrimonio=round(total_patrimonio, 2),
            activo_corriente=round(total_act_corr, 2),
            pasivo_corriente=round(total_pas_corr, 2)
        )

        # Validación de la ecuación fundamental: Total Activo = Total Pasivo + Total Patrimonio
        total_pasivo_patrimonio = total_pasivo + total_patrimonio
        diff = total_activo - total_pasivo_patrimonio
        alerts: List[str] = []
        is_valid = True

        if abs(diff) > tolerance:
            is_valid = False
            lado = "Activo mayor que Pasivo + Patrimonio" if diff > 0 else "Pasivo + Patrimonio mayor que Activo"
            alerts.append(
                f"Descuadre contable detectado: Total Activo ({round(total_activo, 2)}) != "
                f"Total Pasivo + Patrimonio ({round(total_pasivo_patrimonio, 2)}). "
                f"Diferencia: {round(abs(diff), 2)} ({lado})."
            )

        return BalanceSheetResultDTO(
            is_valid=is_valid,
            alerts=alerts,
            balance=balance_struct,
            metrics_base=metrics_base
        )
