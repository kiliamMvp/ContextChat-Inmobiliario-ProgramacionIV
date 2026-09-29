import json
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase, Client

from .forms import HouseForm
from .logic import detect_intent, validate_data
from .context import get_house_context
from .models import House, Place, HouseDistance, ChatMessage
from .reports import ejecutar_reportes
from .reports import (
    TotalPropiedades,
    PropiedadMasCara,
    PropiedadMasBarata,
    PropiedadesBajoPromedio,
    PropiedadesPorUbicacion,
)
from .report_factory import ReporteFactory
from .services.ollama_service import crear_servicio_ollama


def crear_casas():
    """Crea 3 propiedades de prueba con precios conocidos."""
    h1 = House.objects.create(
        codigo="CASA-001", name="Villa Serena",
        location="Costa Azul", price=480000,
        description="Villa de 3 dormitorios.", dormitorios=3,
    )
    h2 = House.objects.create(
        codigo="CASA-002", name="Ático Mirador Real",
        location="Zona Centro", price=650000,
        description="Ático de 4 habitaciones.", dormitorios=4,
    )
    h3 = House.objects.create(
        codigo="CASA-003", name="Residencial Los Robles",
        location="Bosque Real", price=320000,
        description="Casa familiar.", dormitorios=3,
    )
    return h1, h2, h3


class TestCodigoUnico(TestCase):
    """Valida el identificador único y las validaciones del formulario."""

    def test_codigo_duplicado_da_error(self):
        House.objects.create(
            codigo="CASA-001", name="Una", location="X",
            price=100, description="d", dormitorios=1,
        )
        with self.assertRaises(IntegrityError):
            House.objects.create(
                codigo="CASA-001", name="Otra", location="Y",
                price=200, description="d", dormitorios=1,
            )

    def test_form_rechaza_codigo_duplicado(self):
        House.objects.create(
            codigo="CASA-001", name="Una", location="X",
            price=100, description="d", dormitorios=1,
        )
        form = HouseForm(data={
            'codigo': 'CASA-001', 'name': 'Otra', 'location': 'Y',
            'price': '200', 'description': 'd', 'dormitorios': 1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)

    def test_form_rechaza_precio_negativo(self):
        form = HouseForm(data={
            'codigo': 'CASA-010', 'name': 'Mala', 'location': 'Y',
            'price': '-50', 'description': 'd', 'dormitorios': 1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_form_rechaza_dormitorios_negativos(self):
        form = HouseForm(data={
            'codigo': 'CASA-011', 'name': 'Mala', 'location': 'Y',
            'price': '50', 'description': 'd', 'dormitorios': -2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('dormitorios', form.errors)


class TestReportes(TestCase):
    """Verifica los 5 reportes con datos reales."""

    def setUp(self):
        crear_casas()

    def test_cinco_reportes_con_datos_reales(self):
        resultados = ejecutar_reportes()
        self.assertEqual(len(resultados), 5)
        textos = " ".join(r['resultado'] for r in resultados)
        self.assertIn("3 propiedades registradas", textos)
        self.assertIn("Ático Mirador Real", textos)  # la más cara
        self.assertIn("Residencial Los Robles", textos)  # la más barata
        self.assertIn("Villa Serena", textos)  # bajo el promedio


class TestRestriccionDominio(TestCase):
    """Django debe rechazar preguntas fuera del dominio sin llamar a Ollama."""

    def setUp(self):
        self.client = Client()
        self.house, _, _ = crear_casas()

    def post_pregunta(self, texto):
        return self.client.post(
            f'/chat/{self.house.id}/',
            data=json.dumps({'question': texto}),
            content_type='application/json',
        )

    @patch('chatbot.views.generate_response')
    def test_pregunta_general_se_rechaza(self, mock_ai):
        resp = self.post_pregunta("¿Quién es el presidente de Bolivia?")
        mock_ai.assert_not_called()
        self.assertEqual(
            resp.json()['response'],
            "Solo puedo responder consultas sobre propiedades inmobiliarias y sus datos.",
        )

    @patch('chatbot.views.generate_response')
    def test_capital_francia_se_rechaza(self, mock_ai):
        resp = self.post_pregunta("¿Cuál es la capital de Francia?")
        mock_ai.assert_not_called()
        self.assertEqual(
            resp.json()['response'],
            "Solo puedo responder consultas sobre propiedades inmobiliarias y sus datos.",
        )

    @patch('chatbot.views.generate_response')
    def test_pregunta_inmobiliaria_si_llama_a_la_ia(self, mock_ai):
        mock_ai.return_value = "Cuesta $480,000."
        resp = self.post_pregunta("¿Cuál es el precio de Villa Serena?")
        mock_ai.assert_called_once()
        self.assertEqual(resp.json()['response'], "Cuesta $480,000.")

    def test_detect_intent_bloquea_generales(self):
        self.assertEqual(detect_intent("cual es el precio de Villa Serena"), "price")
        self.assertEqual(detect_intent("quien es el presidente actual de bolivia"), "general")
        contexto = get_house_context(self.house.id)
        valido, _, mensaje = validate_data(contexto, "general")
        self.assertFalse(valido)
        self.assertEqual(
            mensaje,
            "Solo puedo responder consultas sobre propiedades inmobiliarias y sus datos.",
        )


class TestSinDatos(TestCase):
    """Si el dato no existe, se responde el mensaje fijo sin llamar a Ollama."""

    def setUp(self):
        self.client = Client()
        self.house = House.objects.create(
            codigo="CASA-099", name="Casa Vacía",
            location="Ninguna", price=10,
            description="", dormitorios=0,
        )

    @patch('chatbot.views.generate_response')
    def test_dato_faltante(self, mock_ai):
        resp = self.client.post(
            f'/chat/{self.house.id}/',
            data=json.dumps({'question': '¿Qué descripción tiene la propiedad?'}),
            content_type='application/json',
        )
        mock_ai.assert_not_called()
        self.assertEqual(resp.json()['response'], "No tengo ese dato disponible.")

    @patch('chatbot.views.generate_response')
    def test_lugar_no_registrado(self, mock_ai):
        resp = self.client.post(
            f'/chat/{self.house.id}/',
            data=json.dumps({'question': '¿Qué hospitales hay cerca?'}),
            content_type='application/json',
        )
        mock_ai.assert_not_called()
        self.assertEqual(resp.json()['response'], "No tengo ese dato disponible.")


class TestReporteFactory(TestCase):
    """Verifica que la Factory devuelve la estrategia correcta."""

    def setUp(self):
        crear_casas()

    def test_factory_total(self):
        reporte = ReporteFactory.crear("total")
        self.assertIsInstance(reporte, TotalPropiedades)
        self.assertIn("3 propiedades registradas", reporte.calcular())

    def test_factory_mas_cara(self):
        reporte = ReporteFactory.crear("mas_cara")
        self.assertIsInstance(reporte, PropiedadMasCara)
        self.assertIn("Ático Mirador Real", reporte.calcular())

    def test_factory_mas_barata(self):
        reporte = ReporteFactory.crear("mas_barata")
        self.assertIsInstance(reporte, PropiedadMasBarata)
        self.assertIn("Residencial Los Robles", reporte.calcular())

    def test_factory_bajo_promedio(self):
        reporte = ReporteFactory.crear("bajo_promedio")
        self.assertIsInstance(reporte, PropiedadesBajoPromedio)
        self.assertIn("Villa Serena", reporte.calcular())

    def test_factory_por_ubicacion(self):
        reporte = ReporteFactory.crear("por_ubicacion")
        self.assertIsInstance(reporte, PropiedadesPorUbicacion)
        self.assertIn("3 ubicaciones", reporte.calcular())

    def test_factory_tipo_inexistente_da_error(self):
        with self.assertRaises(ValueError):
            ReporteFactory.crear("no_existe")


class TestServicioOllama(TestCase):
    """Pruebas del servicio de Ollama (con mocks, sin encender Ollama)."""

    def setUp(self):
        self.client = Client()
        self.house = House.objects.create(
            codigo="CASA-020", name="Casa Test",
            location="Zona Test", price=100000,
            description="Casa de prueba.", dormitorios=2,
        )
        lugar = Place.objects.create(name="Hospital Test", category="medical")
        HouseDistance.objects.create(
            house=self.house, place=lugar, distance_in_meters=150,
        )

    @patch('chatbot.views.generate_response')
    def test_lugares_cercanos_con_datos_llaman_a_ia(self, mock_ai):
        mock_ai.return_value = "Hospital Test a 150m."
        resp = self.client.post(
            f'/chat/{self.house.id}/',
            data=json.dumps({'question': '¿Qué hospitales hay cerca?'}),
            content_type='application/json',
        )
        mock_ai.assert_called_once()
        self.assertEqual(resp.json()['response'], "Hospital Test a 150m.")

    @patch('chatbot.services.ollama_service.requests.post')
    def test_servicio_usa_casas_qwen(self, mock_post):
        mock_post.return_value.json.return_value = {"response": "Hola."}
        servicio = crear_servicio_ollama()
        servicio.preguntar("¿Precio?", {"name": "X"}, [])
        url_llamada = mock_post.call_args[0][0]
        datos = mock_post.call_args[1]['json']
        self.assertTrue(url_llamada.endswith("/api/generate"))
        self.assertEqual(datos["model"], "casas-qwen2.5")

    @patch('chatbot.services.ollama_service.requests.post')
    def test_ollama_apagado_mensaje_amigable(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("caído")
        servicio = crear_servicio_ollama()
        respuesta = servicio.preguntar("¿Precio?", {"name": "X"}, [])
        self.assertEqual(
            respuesta,
            "No fue posible comunicarse con el servicio de IA local. "
            "Verifique que Ollama esté ejecutándose.",
        )
        self.assertNotIn("Traceback", respuesta)


class TestCRUDyReportes(TestCase):
    """Pruebas básicas de las vistas del CRUD y de reportes."""

    def setUp(self):
        self.client = Client()

    def test_crear_propiedad_valida(self):
        resp = self.client.post('/propiedades/nueva/', {
            'codigo': 'CASA-030', 'name': 'Casa Nueva',
            'location': 'Zona Nueva', 'price': '250000',
            'description': 'Casa de prueba.', 'dormitorios': 2,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(House.objects.filter(codigo='CASA-030').exists())

    def test_crear_propiedad_precio_invalido(self):
        resp = self.client.post('/propiedades/nueva/', {
            'codigo': 'CASA-031', 'name': 'Casa Mala',
            'location': 'Zona Mala', 'price': 'abc',
            'description': 'Casa de prueba.', 'dormitorios': 1,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('price', resp.context['form'].errors)
        self.assertFalse(House.objects.filter(codigo='CASA-031').exists())

    def test_eliminar_propiedad(self):
        casa = House.objects.create(
            codigo="CASA-032", name="Casa Fuera",
            location="Zona Fuera", price=50000,
            description="Casa de prueba.", dormitorios=1,
        )
        resp = self.client.post(f'/propiedades/{casa.id}/eliminar/')
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(House.objects.filter(codigo='CASA-032').exists())

    def test_reportes_responden_200(self):
        crear_casas()
        resp = self.client.get('/reportes/')
        self.assertEqual(resp.status_code, 200)
        resultados = resp.context['resultados']
        self.assertEqual(len(resultados), 5)
        self.assertIn("3 propiedades registradas", resultados[0]['resultado'])


class TestHistorialVisible(TestCase):
    """El historial guardado debe verse al entrar al chat de la propiedad."""

    def setUp(self):
        self.client = Client()
        self.house = House.objects.create(
            codigo="CASA-040", name="Casa Historial",
            location="Zona H", price=90000,
            description="Casa de prueba.", dormitorios=1,
        )

    def test_historial_vacio_muestra_mensaje(self):
        resp = self.client.get(f'/chat/{self.house.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Todavía no hay conversaciones para esta propiedad.")

    def test_historial_guardado_se_muestra_en_orden(self):
        ChatMessage.objects.create(house=self.house, question="Pregunta uno", response="Respuesta uno")
        ChatMessage.objects.create(house=self.house, question="Pregunta dos", response="Respuesta dos")
        resp = self.client.get(f'/chat/{self.house.id}/')
        contenido = resp.content.decode('utf-8')
        self.assertContains(resp, "Historial de conversación")
        self.assertContains(resp, "Pregunta uno")
        self.assertContains(resp, "Respuesta dos")
        self.assertLess(contenido.index("Pregunta uno"), contenido.index("Pregunta dos"))
