"""Reportes predefinidos sobre las propiedades.

Patrón Strategy: cada reporte es una estrategia con el mismo método
calcular(). Así se pueden agregar reportes nuevos sin tocar la vista.
"""
from .models import House
from .report_factory import ReporteFactory


def _formato_precio(valor):
    """Muestra un Decimal como $480,000."""
    return f"${valor:,.0f}"


class Reporte:
    nombre = ""
    descripcion = ""

    def calcular(self):
        raise NotImplementedError


class TotalPropiedades(Reporte):
    nombre = "Total de propiedades registradas"
    descripcion = "Cantidad de propiedades guardadas en la base de datos."

    def calcular(self):
        return f"{House.objects.count()} propiedades registradas."


class PropiedadMasCara(Reporte):
    nombre = "Propiedad más cara"
    descripcion = "La propiedad con el precio más alto."

    def calcular(self):
        casa = House.objects.order_by('-price').first()
        if not casa:
            return "No hay precios disponibles."
        return f"{casa.name} ({casa.codigo}) con precio {casa.precio_formateado()}."


class PropiedadMasBarata(Reporte):
    nombre = "Propiedad más barata"
    descripcion = "La propiedad con el precio más bajo."

    def calcular(self):
        casa = House.objects.order_by('price').first()
        if not casa:
            return "No hay precios disponibles."
        return f"{casa.name} ({casa.codigo}) con precio {casa.precio_formateado()}."


class PropiedadesBajoPromedio(Reporte):
    nombre = "Propiedades con precio inferior al promedio"
    descripcion = "Lista las propiedades que cuestan menos que el promedio."

    def calcular(self):
        casas = list(House.objects.all())
        if not casas:
            return "No hay precios disponibles."
        promedio = sum(c.price for c in casas) / len(casas)
        baratas = [c.name for c in casas if c.price < promedio]
        texto = f"Promedio: {_formato_precio(promedio)}."
        if not baratas:
            return texto + " Ninguna está por debajo."
        return texto + f" Por debajo: {', '.join(baratas)}."


class PropiedadesPorUbicacion(Reporte):
    nombre = "Propiedades agrupadas por ubicación"
    descripcion = "Resume cuántas propiedades hay en cada ubicación."

    def calcular(self):
        casas = House.objects.all()
        if not casas:
            return "No hay propiedades registradas."
        grupos = {}
        for casa in casas:
            grupos[casa.location] = grupos.get(casa.location, 0) + 1
        resumen = "; ".join(f"{lugar}: {n}" for lugar, n in grupos.items())
        return f"{len(grupos)} ubicaciones. {resumen}."


# Lista de estrategias disponibles, creada con la Factory
# para que la vista no conozca las clases concretas.
REPORTES = [ReporteFactory.crear(t) for t in ReporteFactory.tipos()]


def ejecutar_reportes():
    """Ejecuta todos los reportes y devuelve sus resultados."""
    resultados = []
    for reporte in REPORTES:
        resultados.append({
            'nombre': reporte.nombre,
            'descripcion': reporte.descripcion,
            'resultado': reporte.calcular(),
        })
    return resultados
