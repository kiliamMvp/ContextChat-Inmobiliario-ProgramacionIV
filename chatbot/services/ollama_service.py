"""Servicio para hablar con Ollama local.

Patrón Factory: la función crear_servicio_ollama() construye el servicio
ya configurado (URL y modelo). El resto del código no necesita saber
esos detalles, solo usa el servicio.
"""
import os

import requests

URL_DEFECTO = "http://localhost:11434"
MODELO_DEFECTO = "casas-qwen2.5"

RESPUESTA_FUERA_DOMINIO = (
    "Solo puedo responder consultas sobre propiedades inmobiliarias y sus datos."
)
RESPUESTA_SIN_DATOS = "No tengo ese dato disponible."
ERROR_CONEXION = (
    "No fue posible comunicarse con el servicio de IA local. "
    "Verifique que Ollama esté ejecutándose."
)


class OllamaService:
    """Encargado de construir el prompt y llamar a Ollama."""

    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or os.getenv("OLLAMA_URL", URL_DEFECTO)
        self.model = model or os.getenv("OLLAMA_MODEL", MODELO_DEFECTO)

    def construir_prompt(self, pregunta, casa, lugares):
        if lugares:
            lineas = []
            for lugar in lugares:
                cat = lugar.get('category_display') or lugar.get('category', 'Servicio')
                lineas.append(f"- {lugar.get('name')}: {lugar.get('distance_meters')}m ({cat})")
            lugares_txt = "\n".join(lineas)
        else:
            lugares_txt = "- Sin servicios cercanos registrados"

        return f"""DATOS VERIFICADOS DE LA PROPIEDAD:

Código: {casa.get('codigo', '')}
Nombre: {casa.get('name', 'Propiedad')}
Ubicación: {casa.get('location', '')}
Precio: {casa.get('price', '')}
Descripción: {casa.get('description', '')}
Dormitorios: {casa.get('dormitorios', '')}

LUGARES Y SERVICIOS CERCANOS:
{lugares_txt}

PREGUNTA DEL USUARIO:
{pregunta}

Responde solo sobre propiedades inmobiliarias usando únicamente los datos de arriba.
Si el dato pedido no está en los datos, responde exactamente: {RESPUESTA_SIN_DATOS}
Responde siempre en español, de forma breve y clara.
"""

    def preguntar(self, pregunta, casa, lugares):
        """Envía la pregunta con su contexto a Ollama y devuelve la respuesta."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": self.construir_prompt(pregunta, casa, lugares),
            "stream": False,
        }
        try:
            respuesta = requests.post(url, json=payload, timeout=120)
            respuesta.raise_for_status()
            return respuesta.json().get("response", "").strip()
        except requests.exceptions.RequestException:
            return ERROR_CONEXION


def crear_servicio_ollama():
    """Factory: crea el servicio de Ollama con la configuración actual."""
    return OllamaService()
