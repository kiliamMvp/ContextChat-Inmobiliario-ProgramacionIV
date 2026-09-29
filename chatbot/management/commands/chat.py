from django.core.management.base import BaseCommand
from chatbot.context import get_house_context
from chatbot.logic import detect_intent, validate_data
from chatbot.ai import generate_response

class Command(BaseCommand):
    help = 'Chatear sobre una propiedad específica o realizar cualquier consulta'

    def add_arguments(self, parser):
        parser.add_argument('house_id', type=int, help='ID de la propiedad')
        parser.add_argument('question', type=str, help='Pregunta a realizar')

    def handle(self, *args, **options):
        house_id = options['house_id']
        question = options['question']

        # 1. Cargar contexto
        context = get_house_context(house_id)
        if not context:
            self.stdout.write("Propiedad no encontrada.")
            return

        # 2. Detectar intención
        intent = detect_intent(question)

        # 3. Validar datos
        is_valid, relevant_data, manual_response = validate_data(context, intent)

        if not is_valid:
            self.stdout.write(manual_response)
        else:
            # 4. Llamar a la IA
            response = generate_response(context['house'], relevant_data, question)
            self.stdout.write(response)

