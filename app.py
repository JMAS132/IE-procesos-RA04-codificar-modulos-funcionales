from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from database import eliminar_mascota, guardar_mascota, init_db, obtener_mascotas
from models import Mascota

app = Flask(__name__)
app.secret_key = "patitas-sanas-secret-key"
init_db()


@app.route("/")
def index():
    mascotas = obtener_mascotas()
    return render_template("index.html", mascotas=mascotas)


@app.route("/agregar", methods=["POST"])
def agregar():
    # Validación básica del formulario para evitar registros vacíos o inconsistentes
    nombre = request.form.get("nombre", "").strip()
    especie = request.form.get("especie", "").strip()
    edad = request.form.get("edad", "0").strip()
    nombre_propietario = request.form.get("nombre_propietario", "").strip()
    telefono_propietario = request.form.get("telefono_propietario", "").strip()

    if not nombre or not especie:
        flash("Debe ingresar el nombre y la especie de la mascota.")
        return redirect(url_for("index"))

    # La edad se intenta convertir a entero; si no es válida, se conserva un valor seguro
    try:
        edad_value = int(edad or 0)
        if edad_value < 0:
            edad_value = 0
    except ValueError:
        edad_value = 0

    # Se guardan los datos con un formato consistente para la fecha y el nombre del propietario
    mascota = Mascota(
        nombre=nombre,
        especie=especie,
        edad=edad_value,
        nombre_propietario=nombre_propietario,
        telefono_propietario=telefono_propietario,
        fecha_registro=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Recoger los datos en una estructura del modelo antes de insertarlos en SQLite
    guardar_mascota(mascota)
    flash("Mascota registrada correctamente.")
    return redirect(url_for("index"))


@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    eliminar_mascota(id)
    flash("Mascota eliminada del registro.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
