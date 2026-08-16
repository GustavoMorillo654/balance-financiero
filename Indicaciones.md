# Fundamentos teóricos y matemáticos de la aplicación

## Propósito del modelo

La aplicación transforma cuentas contables en un Balance General, comprueba su consistencia, calcula indicadores financieros y estima una categoría de crédito. Todas las cantidades monetarias conservan la moneda del archivo de origen; las proporciones se expresan como decimales, por lo que `0,35` equivale a `35 %`.

El flujo conceptual es:

```text
Cuentas → Clasificación → Depreciación → Balance → Razones → Puntaje Z
```

## Clasificación contable

Cada cuenta se asigna a una categoría económica:

- **Activo corriente (AC):** efectivo, bancos, inventarios y cuentas por cobrar; se espera convertirlos en efectivo o consumirlos en el corto plazo.
- **Activo no corriente (ANC):** terrenos, maquinaria, equipos y otros recursos de uso prolongado.
- **Pasivo corriente (PC):** obligaciones exigibles en el corto plazo.
- **Pasivo no corriente (PNC):** deudas y obligaciones de largo plazo.
- **Patrimonio aportado (P):** capital, reservas y resultados acumulados.
- **Ingresos (I) y egresos (E):** cuentas utilizadas para determinar el resultado del período.

La aplicación prioriza el tipo contable indicado en el CSV. Si falta, lo infiere a partir del nombre de la cuenta y su significado financiero.

## Depreciación y valor neto

Los activos no corrientes con vida útil válida se deprecian mediante línea recta:

$$
D_a = \frac{C - V_r}{n}
$$

donde $D_a$ es la depreciación anual, $C$ el costo histórico, $V_r$ el valor residual y $n$ la vida útil en años. Actualmente se toma $V_r=0$ y un período transcurrido. Por tanto:

$$
D_{acum} = D_a \times t
$$

$$
V_n = C - D_{acum}
$$

La depreciación acumulada nunca puede superar el costo histórico. Los terrenos no se deprecian, y un activo sin vida útil válida conserva su saldo como valor neto.

## Resultado del período y Balance General

Cuando existen cuentas de resultados, la utilidad neta se calcula como:

$$
U = I - E - D
$$

donde $D$ es la depreciación del período. La utilidad se incorpora al patrimonio como **Utilidad Neta del Ejercicio**.

Los totales del balance son:

$$
A = AC + ANC_{neto}
$$

$$
L = PC + PNC
$$

$$
PT = P + U
$$

La ecuación contable fundamental exige:

$$
A = L + PT
$$

La diferencia se define como $\Delta=A-(L+PT)$. El balance es válido cuando $|\Delta|\leq0,001$; fuera de esa tolerancia se reporta un descuadre.

## Conciliación temporal

El modo **estricto** conserva los importes originales. Si el balance no cuadra, los indicadores pueden calcularse, pero no se emite dictamen de crédito.

El modo **conciliación** crea en memoria una cuenta puente:

$$
J=(L+PT)-A
$$

Luego actualiza $AC'=AC+J$ y $A'=A+J$, de manera que $A'=L+PT$. Este ajuste no escribe ni corrige el CSV. Su única finalidad es permitir el análisis matemático, queda identificado como temporal y afecta las razones que utilizan activo corriente o activo total. Por ello, el resultado conciliado debe interpretarse junto con la alerta del descuadre original.

## Razones de liquidez

Miden la capacidad para atender obligaciones de corto plazo:

| Indicador | Fórmula | Interpretación |
|---|---|---|
| Razón corriente | $AC/PC$ | Unidades de activo corriente por cada unidad de deuda corriente. |
| Prueba ácida | $(AC-Inventario)/PC$ | Liquidez sin depender de la venta del inventario. |
| Capital de trabajo | $AC-PC$ | Excedente monetario de recursos corrientes. |

## Razones de apalancamiento

Describen la estructura de financiación:

| Indicador | Fórmula | Interpretación |
|---|---|---|
| Endeudamiento | $L/A$ | Proporción de activos financiada por terceros. |
| Pasivo/Patrimonio | $L/PT$ | Deuda por cada unidad de patrimonio. |
| Autonomía financiera | $PT/A$ | Proporción de activos financiada con recursos propios. |
| Apalancamiento interno | $PT/L$ | Recursos propios por cada unidad aportada por terceros. |

## Razones de actividad

Miden la velocidad de utilización o recuperación de recursos. Sea $T$ la duración configurada del período, normalmente 365 días:

| Indicador | Fórmula |
|---|---|
| Rotación de inventarios | $Costos/Inventario$ |
| Días de inventario | $T/Rotación\ de\ inventarios$ |
| Rotación de activos | $Ventas/A$ |
| Rotación de cuentas por cobrar | $Ventas/Cuentas\ por\ cobrar$ |
| Período de cobro | $T/Rotación\ de\ cuentas\ por\ cobrar$ |

Una rotación expresa cuántas veces ocurre el ciclo durante el período; su conversión a días expresa el tiempo promedio del ciclo.

## Razones de rentabilidad

Relacionan la utilidad neta con ventas, activos y patrimonio:

$$
Margen\ neto=\frac{U}{Ventas},\qquad ROA=\frac{U}{A},\qquad ROE=\frac{U}{PT}
$$

El margen neto mide la utilidad obtenida por unidad vendida; el ROA mide el rendimiento de los recursos controlados y el ROE el rendimiento contable de los recursos propios.

## Modelo de evaluación crediticia

El puntaje utiliza dos indicadores ya calculados:

$$
X_1=\frac{AC}{PC},\qquad X_2=\frac{PT}{L}
$$

$$
Z=0,4X_1+0,6X_2
$$

La clasificación implementada es:

- $Z>1,4$: **Crédito excelente**.
- $0,66\leq Z\leq1,4$: **Crédito de riesgo normal**.
- $Z<0,66$: **Crédito malo**.

El puntaje queda como `N/D` si el balance está descuadrado en modo estricto, si falta alguno de los dos indicadores o si su denominador es cero. La aplicación nunca sustituye esos casos por infinito, cero artificial o `NaN`.

## Ejemplo matemático con `datos.csv`

La maquinaria cuesta 80.000 y tiene vida útil de 10 años, así que su depreciación es $80.000/10=8.000$ y su valor neto es 72.000. Junto con el terreno de 120.000, el activo no corriente neto es 192.000. El activo corriente original es 100.000, por lo que $A=292.000$.

Los pasivos suman 120.000. La utilidad es $250.000-160.000-8.000=82.000$; al añadirla al patrimonio previo de 120.000 se obtiene $PT=202.000$. Entonces:

$$
292.000\neq120.000+202.000=322.000
$$

La conciliación añade temporalmente $J=30.000$ al activo corriente. Así, $AC'=130.000$ y $A'=322.000$. Para el modelo de crédito:

$$
X_1=\frac{130.000}{60.000}=2,1667
$$

$$
X_2=\frac{202.000}{120.000}=1,6833
$$

$$
Z=0,4(2,1667)+0,6(1,6833)=1,8767
$$

Como $1,8767>1,4$, el resultado es **Crédito excelente**, condicionado a que el ajuste de 30.000 sea revisado y respaldado contablemente.

## Alcance de la interpretación

Los indicadores describen matemáticamente los datos recibidos; no verifican por sí solos que las cuentas sean reales, completas o auditadas. El puntaje Z es una herramienta académica de apoyo y no reemplaza el análisis profesional de solvencia, flujo de caja, historial de pagos, garantías ni contexto económico.
