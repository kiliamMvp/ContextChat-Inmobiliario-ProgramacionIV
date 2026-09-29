import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contextchat.settings')
django.setup()

from chatbot.models import House, Place, HouseDistance

def create_data():
    # Limpieza previa
    HouseDistance.objects.all().delete()
    House.objects.all().delete()
    Place.objects.all().delete()

    print("Generando datos de prueba en español...")

    # Lugares y servicios
    hospital_central = Place.objects.create(name="Hospital Universitario Central", category="medical")
    clinica_salud = Place.objects.create(name="Centro Médico San Lucas", category="medical")
    colegio_los_pinos = Place.objects.create(name="Colegio Bilingüe Los Pinos", category="school")
    instituto_real = Place.objects.create(name="Instituto Tecnológico Moderno", category="school")
    metro_central = Place.objects.create(name="Estación de Metro Central", category="transportation")
    tren_costa = Place.objects.create(name="Terminal de Trenes y Buses", category="transportation")
    mall_gran_plaza = Place.objects.create(name="Centro Comercial Gran Plaza", category="shopping")

    # Propiedad 1: Villa Serena
    house1 = House.objects.create(
        codigo="CASA-001",
        name="Villa Serena",
        location="Av. Las Palmeras 240, Costa Azul",
        price=480000,
        description="Hermosa villa contemporánea de 3 dormitorios y 2 baños con jardín privado, acabados de mármol y amplia terraza con excelente iluminación natural.",
        dormitorios=3,
    )
    HouseDistance.objects.create(house=house1, place=clinica_salud, distance_in_meters=450)
    HouseDistance.objects.create(house=house1, place=colegio_los_pinos, distance_in_meters=750)
    HouseDistance.objects.create(house=house1, place=metro_central, distance_in_meters=300)
    HouseDistance.objects.create(house=house1, place=mall_gran_plaza, distance_in_meters=900)

    # Propiedad 2: Ático Mirador Real
    house2 = House.objects.create(
        codigo="CASA-002",
        name="Ático Mirador Real",
        location="Paseo de la Castellana 112, Zona Centro",
        price=650000,
        description="Exclusivo ático dúplex con vistas panorámicas de la ciudad, 4 habitaciones, domótica inteligente y terraza privada de 60 metros cuadrados.",
        dormitorios=4,
    )
    HouseDistance.objects.create(house=house2, place=hospital_central, distance_in_meters=350)
    HouseDistance.objects.create(house=house2, place=instituto_real, distance_in_meters=600)
    HouseDistance.objects.create(house=house2, place=metro_central, distance_in_meters=200)
    HouseDistance.objects.create(house=house2, place=mall_gran_plaza, distance_in_meters=400)

    # Propiedad 3: Residencial Los Robles
    house3 = House.objects.create(
        codigo="CASA-003",
        name="Residencial Los Robles",
        location="Calle El Robledal 45, Bosque Real",
        price=320000,
        description="Acogedora casa familiar de 3 plantas, cocina equipada, patio con barbacoa, garaje para 2 vehículos y acceso a piscina comunitaria.",
        dormitorios=3,
    )
    HouseDistance.objects.create(house=house3, place=clinica_salud, distance_in_meters=900)
    HouseDistance.objects.create(house=house3, place=colegio_los_pinos, distance_in_meters=400)
    HouseDistance.objects.create(house=house3, place=tren_costa, distance_in_meters=350)

    print(f"¡Datos creados con éxito! Propiedades añadidas: {house1.name} (ID: {house1.id}), {house2.name} (ID: {house2.id}), {house3.name} (ID: {house3.id})")

if __name__ == "__main__":
    create_data()
