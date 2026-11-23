import math
import os
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    error = None

    if request.method == "POST":
        try:
            ingreso = float(request.form.get("ingreso", 0) or 0)
            gastos_fijos = float(request.form.get("gastos_fijos", 0) or 0)
            gastos_variables = float(request.form.get("gastos_variables", 0) or 0)
            meta_raw = request.form.get("meta", "").strip()
            meta = float(meta_raw) if meta_raw else 0.0

            if ingreso <= 0:
                error = "Ingresa un ingreso mensual mayor que 0."
            elif gastos_fijos < 0 or gastos_variables < 0 or meta < 0:
                error = "Los gastos y la meta no pueden ser negativos."
            else:
                necesidades = round(ingreso * 0.50, 2)
                deseos = round(ingreso * 0.30, 2)
                ahorro_sugerido = round(ingreso * 0.20, 2)

                gastos_totales = round(gastos_fijos + gastos_variables, 2)
                saldo_real = round(ingreso - gastos_totales, 2)

                meses_meta = None
                if meta > 0:
                    capacidad_ahorro = saldo_real if saldo_real > 0 else ahorro_sugerido
                    if capacidad_ahorro > 0:
                        meses_meta = math.ceil(meta / capacidad_ahorro)

                resultado = {
                    "ingreso": round(ingreso, 2),
                    "necesidades": necesidades,
                    "deseos": deseos,
                    "ahorro_sugerido": ahorro_sugerido,
                    "gastos_totales": gastos_totales,
                    "saldo_real": saldo_real,
                    "meta": round(meta, 2) if meta > 0 else None,
                    "meses_meta": meses_meta,
                }
        except ValueError:
            error = "Por favor escribe números válidos en los campos."

    return render_template("index.html", resultado=resultado, error=error)


@app.route("/ahorro", methods=["GET", "POST"])
def ahorro():
    resultado = None
    error = None

    if request.method == "POST":
        try:
            capital = float(request.form.get("capital", 0) or 0)
            aporte = float(request.form.get("aporte", 0) or 0)
            tasa = float(request.form.get("tasa", 0) or 0)
            meses = int(float(request.form.get("meses", 0) or 0))

            if capital < 0 or aporte < 0 or tasa < 0 or meses <= 0:
                error = "Usa valores positivos y un plazo en meses mayor que 0."
            elif meses > 600:
                error = "Ingresa un plazo de hasta 600 meses (50 años)."
            else:
                tasa_mensual = (tasa / 100) / 12
                saldo = capital
                historial_anual = []

                for mes in range(1, meses + 1):
                    saldo = saldo * (1 + tasa_mensual) + aporte
                    if mes % 12 == 0 or mes == meses:
                        aportado_hasta_ahora = capital + (aporte * mes)
                        interes_hasta_ahora = saldo - aportado_hasta_ahora
                        anios_enteros = mes // 12
                        meses_extra = mes % 12

                        if anios_enteros > 0 and meses_extra == 0:
                            etiqueta_tiempo = f"{anios_enteros} {'año' if anios_enteros == 1 else 'años'}"
                        elif anios_enteros > 0 and meses_extra > 0:
                            etiqueta_tiempo = f"{anios_enteros} {'año' if anios_enteros == 1 else 'años'} y {meses_extra} {'mes' if meses_extra == 1 else 'meses'}"
                        else:
                            etiqueta_tiempo = f"{meses_extra} {'mes' if meses_extra == 1 else 'meses'}"

                        historial_anual.append({
                            "mes": mes,
                            "etiqueta_tiempo": etiqueta_tiempo,
                            "saldo": round(saldo, 2),
                            "aportado": round(aportado_hasta_ahora, 2),
                            "interes": round(interes_hasta_ahora, 2),
                        })

                total_aportado = capital + (aporte * meses)
                ganancia = saldo - total_aportado
                pct_ganancia = (ganancia / saldo * 100) if saldo > 0 else 0.0

                resultado = {
                    "capital": round(capital, 2),
                    "aporte": round(aporte, 2),
                    "tasa": round(tasa, 2),
                    "meses": meses,
                    "total": round(saldo, 2),
                    "total_aportado": round(total_aportado, 2),
                    "ganancia": round(ganancia, 2),
                    "pct_ganancia": round(pct_ganancia, 1),
                    "historial": historial_anual,
                }
        except ValueError:
            error = "Revisa que todos los campos tengan números válidos."

    return render_template("ahorro.html", resultado=resultado, error=error)


@app.route("/guias")
def guias():
    return render_template("guias.html")


@app.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    modo_debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=puerto, debug=modo_debug)