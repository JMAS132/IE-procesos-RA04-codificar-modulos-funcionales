import sqlite3
from datetime import datetime
from pathlib import Path

from models import Mascota

DB_PATH = Path(__file__).resolve().parent / "patitassanas.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        # Se crea la tabla demandada en la especificación: pacientes.
        # Si existía una versión anterior con el nombre mascotas, se migra la información.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                especie TEXT NOT NULL,
                edad INTEGER,
                nombre_propietario TEXT,
                telefono_propietario TEXT,
                fecha_registro TEXT NOT NULL
            )
            """
        )

        columnas = [
            row[1]
            for row in conn.execute("PRAGMA table_info(pacientes)").fetchall()
        ]

        if "nombre_propietario" not in columnas:
            conn.execute(
                "ALTER TABLE pacientes ADD COLUMN nombre_propietario TEXT"
            )
        if "telefono_propietario" not in columnas:
            conn.execute(
                "ALTER TABLE pacientes ADD COLUMN telefono_propietario TEXT"
            )

        tablas_existentes = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]

        if "mascotas" in tablas_existentes and not conn.execute(
            "SELECT COUNT(*) FROM pacientes"
        ).fetchone()[0]:
            rows = conn.execute(
                """
                SELECT id, nombre, especie, edad, nombre_propietario, telefono_propietario, fecha_registro
                FROM mascotas
                """
            ).fetchall()

            for row in rows:
                conn.execute(
                    """
                    INSERT INTO pacientes (id, nombre, especie, edad, nombre_propietario, telefono_propietario, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["id"],
                        row["nombre"],
                        row["especie"],
                        row["edad"],
                        row["nombre_propietario"],
                        row["telefono_propietario"],
                        row["fecha_registro"],
                    ),
                )

        conn.commit()


def obtener_mascotas() -> list[Mascota]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, nombre, especie, edad, nombre_propietario, telefono_propietario, fecha_registro
            FROM pacientes
            ORDER BY fecha_registro DESC
            """
        ).fetchall()

    mascotas = []
    for row in rows:
        mascotas.append(
            Mascota(
                id=row["id"],
                nombre=row["nombre"],
                especie=row["especie"],
                edad=row["edad"] or 0,
                nombre_propietario=row["nombre_propietario"] or "",
                telefono_propietario=row["telefono_propietario"] or "",
                fecha_registro=row["fecha_registro"],
            )
        )
    return mascotas


def guardar_mascota(mascota: Mascota) -> None:
    if not mascota.fecha_registro:
        mascota.fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Las consultas usan parámetros (?, ?, ...) para evitar inyección SQL y mantener datos seguros.
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO pacientes (nombre, especie, edad, nombre_propietario, telefono_propietario, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                mascota.nombre,
                mascota.especie,
                mascota.edad,
                mascota.nombre_propietario,
                mascota.telefono_propietario,
                mascota.fecha_registro,
            ),
        )
        conn.commit()


def eliminar_mascota(mascota_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM pacientes WHERE id = ?", (mascota_id,))
        conn.commit()
