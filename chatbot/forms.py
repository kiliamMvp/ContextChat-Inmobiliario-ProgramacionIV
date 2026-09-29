from django import forms
from .models import House


class HouseForm(forms.ModelForm):
    """Formulario para crear y editar propiedades, con validaciones básicas."""

    class Meta:
        model = House
        fields = ['codigo', 'name', 'location', 'price', 'description', 'dormitorios']
        labels = {
            'codigo': 'Código',
            'name': 'Nombre',
            'location': 'Ubicación',
            'price': 'Precio (ej: 480000)',
            'description': 'Descripción',
            'dormitorios': 'Dormitorios',
        }

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip()
        if not codigo:
            raise forms.ValidationError("El código es obligatorio.")
        return codigo

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("El precio es obligatorio.")
        if price < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return price

    def clean_dormitorios(self):
        dormitorios = self.cleaned_data['dormitorios']
        if dormitorios is None or dormitorios < 0:
            raise forms.ValidationError("Los dormitorios no pueden ser negativos.")
        return dormitorios
