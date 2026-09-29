from django.contrib import admin
from .models import House, Place, HouseDistance, ChatMessage


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'name', 'location', 'price', 'dormitorios')
    search_fields = ('codigo', 'name', 'location')


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)


@admin.register(HouseDistance)
class HouseDistanceAdmin(admin.ModelAdmin):
    list_display = ('house', 'place', 'distance_in_meters')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('house', 'question', 'created_at')
    readonly_fields = ('created_at',)
