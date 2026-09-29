from django.db import models

class House(models.Model):
    codigo = models.CharField(max_length=20, unique=True, default="SIN-CODIGO")
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    dormitorios = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.codigo} - {self.name}"

    def precio_formateado(self):
        """Devuelve el precio como texto legible, ej: $480,000."""
        return f"${self.price:,.0f}"

class Place(models.Model):
    CATEGORY_CHOICES = [
        ('medical', 'Servicios Médicos'),
        ('school', 'Colegios y Educación'),
        ('transportation', 'Transporte'),
        ('shopping', 'Centros Comerciales y Tiendas'),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class HouseDistance(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='distances')
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    distance_in_meters = models.IntegerField()

    def __str__(self):
        return f"{self.place.name} está a {self.distance_in_meters}m de {self.house.name}"

class ChatMessage(models.Model):
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    question = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Chat - {self.house.name} - {self.created_at}"
