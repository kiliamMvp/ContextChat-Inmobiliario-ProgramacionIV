from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
import json
import csv
import logging
from .context import get_house_context
from .logic import detect_intent, validate_data
from .ai import generate_response
from .models import House, ChatMessage
from .forms import HouseForm
from .reports import ejecutar_reportes
from .pdf_export import generate_chat_pdf

logger = logging.getLogger(__name__)

def index(request):
    houses = House.objects.all()
    return render(request, 'chatbot/index.html', {'houses': houses})

def chat_view(request, house_id):
    # 1. Cargar contexto de la casa
    context = get_house_context(house_id)
    if not context:
        return render(request, 'chatbot/404.html', status=404)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get('question', '').strip()

            if not question:
                return JsonResponse({"response": "Por favor, escribe una pregunta para comenzar."})
            
            # 2. Detectar intención
            intent = detect_intent(question)

            # 3. Validar datos
            is_valid, relevant_data, manual_response = validate_data(context, intent)

            if not is_valid:
                response = manual_response
            else:
                # 4. Llamar a la IA (Ollama)
                response = generate_response(context['house'], relevant_data, question)

            # 5. Guardar en el historial persistente de la conversación
            ChatMessage.objects.create(
                house_id=house_id,
                question=question,
                response=response
            )

            return JsonResponse({"response": response})

        except Exception as e:
            logger.exception("Error interno en chat_view")
            return JsonResponse({"error": "Ocurrió un error interno. Intente de nuevo."}, status=500)

    # Cargar historial existente de mensajes de esta propiedad
    historial = ChatMessage.objects.filter(house_id=house_id).order_by('created_at')

    # Renderizar la interfaz del chat con datos completos y el historial de mensajes
    return render(request, 'chatbot/chat.html', {
        'house': context['house'],
        'nearby_places': context['nearby_places'],
        'house_id': house_id,
        'messages': historial,
    })

def export_chat_csv(request, house_id):
    """Exporta el historial de conversación de la propiedad a un archivo CSV."""
    house = get_object_or_404(House, pk=house_id)
    messages = ChatMessage.objects.filter(house=house).order_by('created_at')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="historial_chat_casa_{house_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Mensaje', 'Fecha y Hora', 'Propiedad', 'Pregunta del Usuario', 'Respuesta de la IA'])

    for msg in messages:
        writer.writerow([
            msg.id,
            msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            house.name,
            msg.question,
            msg.response
        ])

    return response

def export_chat_pdf(request, house_id):
    """Exporta el historial de conversación de la propiedad a un archivo PDF."""
    house = get_object_or_404(House, pk=house_id)
    messages = ChatMessage.objects.filter(house=house).order_by('created_at')

    pdf_bytes = generate_chat_pdf(house, messages)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="historial_chat_casa_{house_id}.pdf"'
    return response


# ---------------- CRUD de propiedades ----------------

def house_detail(request, house_id):
    """Muestra el detalle de una propiedad."""
    house = get_object_or_404(House, pk=house_id)
    return render(request, 'chatbot/house_detail.html', {'house': house})


def house_create(request):
    """Crea una propiedad nueva."""
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            house = form.save()
            messages.success(request, f"Propiedad {house.codigo} creada correctamente.")
            return redirect('house_detail', house_id=house.id)
        messages.error(request, "Revise los errores del formulario.")
    else:
        form = HouseForm()
    return render(request, 'chatbot/house_form.html', {'form': form, 'titulo': 'Nueva propiedad'})


def house_update(request, house_id):
    """Edita una propiedad existente."""
    house = get_object_or_404(House, pk=house_id)
    if request.method == 'POST':
        form = HouseForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, f"Propiedad {house.codigo} actualizada correctamente.")
            return redirect('house_detail', house_id=house.id)
        messages.error(request, "Revise los errores del formulario.")
    else:
        form = HouseForm(instance=house)
    return render(request, 'chatbot/house_form.html', {'form': form, 'titulo': f'Editar {house.codigo}'})


def house_delete(request, house_id):
    """Elimina una propiedad (pide confirmación)."""
    house = get_object_or_404(House, pk=house_id)
    if request.method == 'POST':
        codigo = house.codigo
        house.delete()
        messages.success(request, f"Propiedad {codigo} eliminada correctamente.")
        return redirect('index')
    return render(request, 'chatbot/house_confirm_delete.html', {'house': house})


def reportes_view(request):
    """Muestra los 5 reportes predefinidos con datos reales."""
    resultados = ejecutar_reportes()
    return render(request, 'chatbot/reportes.html', {'resultados': resultados})
