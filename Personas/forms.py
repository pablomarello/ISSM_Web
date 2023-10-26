from django import forms
from .models import Persona, Contacto

class FormPersona(forms.ModelForm):
    class Meta:
        model=Persona
        fields='__all__'

class FormContacto(forms.ModelForm):
    class Meta:
        model = Contacto
        fields= '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={'type':'email'}),
        }