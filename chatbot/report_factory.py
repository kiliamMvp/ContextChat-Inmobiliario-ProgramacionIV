"""Factory de reportes (segundo patrón de diseño).

Crea los objetos de reporte (las estrategias de reports.py) a partir de
un nombre corto, para que la vista no conozca las clases concretas.

Uso:
    reporte = ReporteFactory.crear("mas_cara")
    reporte.calcular()

Nota: el import está dentro del método para evitar un import circular,
porque reports.py también usa esta Factory para armar su lista.
"""


class ReporteFactory:
    """Factory sencilla: tipo (texto) -> instancia de Reporte."""

    @staticmethod
    def crear(tipo):
        # Import local: evita el import circular con reports.py.
        from .reports import (
            TotalPropiedades,
            PropiedadMasCara,
            PropiedadMasBarata,
            PropiedadesBajoPromedio,
            PropiedadesPorUbicacion,
        )
        if tipo == "total":
            return TotalPropiedades()
        if tipo == "mas_cara":
            return PropiedadMasCara()
        if tipo == "mas_barata":
            return PropiedadMasBarata()
        if tipo == "bajo_promedio":
            return PropiedadesBajoPromedio()
        if tipo == "por_ubicacion":
            return PropiedadesPorUbicacion()
        raise ValueError(f"Reporte desconocido: {tipo}")

    @staticmethod
    def tipos():
        """Nombres cortos de todos los reportes disponibles."""
        return ["total", "mas_cara", "mas_barata", "bajo_promedio", "por_ubicacion"]
