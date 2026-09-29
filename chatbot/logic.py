from .services.ollama_service import RESPUESTA_FUERA_DOMINIO, RESPUESTA_SIN_DATOS
import re


def detect_intent(question):
    """
    Detecta la intención de la pregunta.
    Solo permite temas relacionados con propiedades inmobiliarias
    y lugares cercanos.
    """
    q = question.lower()

    # Operaciones matemáticas (ej: "cuánto es 25 x 30") no son del dominio.
    if re.search(r'\d\s*[x\*\+\-/]\s*\d', q):
        return 'general'

    if any(w in q for w in [
        'hospital', 'medical', 'doctor', 'clinic', 'emergency',
        'médico', 'medico', 'salud', 'clinica', 'clínica',
        'urgencia', 'hospitales'
    ]):
        return 'medical'

    elif any(w in q for w in [
        'school', 'university', 'college', 'education', 'kindergarten',
        'escuela', 'colegio', 'universidad', 'educación', 'educacion',
        'instituto', 'colegios', 'escuelas'
    ]):
        return 'school'

    elif any(w in q for w in [
        'transport', 'bus', 'train', 'metro', 'subway', 'station',
        'transporte', 'autobús', 'autobus', 'tren', 'estación',
        'estacion', 'parada', 'movilidad'
    ]):
        return 'transportation'

    elif any(w in q for w in [
        'shop', 'mall', 'grocery', 'market', 'store', 'tienda',
        'supermercado', 'mercado', 'centro comercial', 'compras',
        'comercio'
    ]):
        return 'shopping'

    elif any(w in q for w in [
        'family', 'kid', 'child', 'familia', 'hijo', 'niño',
        'niña', 'hijos', 'niños', 'familiar'
    ]):
        return 'family'

    elif any(w in q for w in [
        'price', 'precio', 'cost', 'coste', 'cuesta', 'valor',
        'cuánto', 'cuanto', 'tarifa'
    ]):
        return 'price'

    elif any(w in q for w in [
        'location', 'ubicación', 'ubicacion', 'ubicado', 'dónde',
        'donde', 'dirección', 'direccion', 'zona', 'lugar'
    ]):
        return 'location'

    elif any(w in q for w in [
        'description', 'descripción', 'descripcion', 'características',
        'caracteristicas', 'details', 'detalles', 'habitaciones',
        'dormitorio', 'dormitorios',
        'cuartos', 'baños', 'espacios', 'casa', 'propiedad',
        'inmueble', 'vivienda'
    ]):
        return 'description'

    return 'general'


def validate_data(context, intent):
    """
    Valida si la pregunta pertenece al tema permitido.
    Si está fuera del dominio, se rechaza SIN llamar a Ollama.
    Si falta el dato, se avisa con el mensaje fijo.
    """

    if not context or not context.get('exists'):
        return False, [], "Propiedad no encontrada."

    casa = context.get('house', {})
    places = context.get('nearby_places', [])

    # Preguntas relacionadas directamente con la propiedad.
    # Si el dato no existe, no se llama a la IA.
    campos = {'price': 'price', 'location': 'location', 'description': 'description'}
    if intent in campos:
        if not str(casa.get(campos[intent], '')).strip():
            return False, [], RESPUESTA_SIN_DATOS
        return True, places, None

    # Preguntas sobre familias (usan colegios cercanos)
    if intent == 'family':
        relevant = [
            p for p in places
            if p.get('category') == 'school'
        ]
        if not relevant:
            return False, [], RESPUESTA_SIN_DATOS
        return True, relevant, None

    # Preguntas sobre lugares cercanos.
    # Si no hay lugares de ese tipo, no se llama a la IA.
    if intent in ['medical', 'school', 'transportation', 'shopping']:
        relevant = [
            p for p in places
            if p.get('category') == intent
        ]
        if not relevant:
            return False, [], RESPUESTA_SIN_DATOS
        return True, relevant, None

    # Cualquier otro tema queda bloqueado sin llamar a Ollama.
    return False, [], RESPUESTA_FUERA_DOMINIO
