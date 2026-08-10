from dataclasses import dataclass
from typing import Optional


@dataclass
class Mascota:
    id: Optional[int] = None
    nombre: str = ""
    especie: str = ""
    edad: int = 0
    nombre_propietario: str = ""
    telefono_propietario: str = ""
    fecha_registro: str = ""

    @property
    def resumen(self) -> str:
        return f"{self.nombre} · {self.especie} · {self.nombre_propietario}"
