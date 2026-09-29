from .models import House, HouseDistance

def get_house_context(house_id):
    """
    Fetches house data and related places tailored for the chatbot.
    Uses select_related to optimize database access.
    Returns a unified, immutable dictionary context.
    """
    try:
        house = House.objects.get(id=house_id)
    except House.DoesNotExist:
        return None

    # CRITICAL: The requested select_related join
    distances = HouseDistance.objects.select_related("place").filter(house=house)

    # Flatten into in-memory context
    places_data = []
    for dist in distances:
        places_data.append({
            "name": dist.place.name,
            "category": dist.place.category,
            "distance_meters": dist.distance_in_meters,
            "category_display": dist.place.get_category_display()
        })

    # Immutable dictionary serving as the ONLY source of truth
    context = {
        "house": {
            "codigo": house.codigo,
            "name": house.name,
            "location": house.location,
            "price": house.precio_formateado(),
            "description": house.description,
            "dormitorios": house.dormitorios,
        },
        "nearby_places": places_data,
        "exists": True
    }
    
    return context
