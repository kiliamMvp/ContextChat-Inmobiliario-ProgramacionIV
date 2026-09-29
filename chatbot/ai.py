"""Compatibilidad: esta función ahora usa el servicio de Ollama.

Se mantiene para no romper las vistas y el comando de chat que ya la usan.
"""
from .services.ollama_service import crear_servicio_ollama


def generate_response(house_info, relevant_data, user_question):
    """
    Genera respuestas utilizando el modelo personalizado de Ollama.
    El modelo está restringido a consultas sobre propiedades inmobiliarias.
    """
    servicio = crear_servicio_ollama()
    return servicio.preguntar(user_question, house_info, relevant_data)
