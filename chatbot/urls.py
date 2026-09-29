from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('propiedades/nueva/', views.house_create, name='house_create'),
    path('propiedades/<int:house_id>/', views.house_detail, name='house_detail'),
    path('propiedades/<int:house_id>/editar/', views.house_update, name='house_update'),
    path('propiedades/<int:house_id>/eliminar/', views.house_delete, name='house_delete'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('chat/<int:house_id>/', views.chat_view, name='chat'),
    path('chat/<int:house_id>/exportar/csv/', views.export_chat_csv, name='export_chat_csv'),
    path('chat/<int:house_id>/exportar/pdf/', views.export_chat_pdf, name='export_chat_pdf'),
]
