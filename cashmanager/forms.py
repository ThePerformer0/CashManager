from django import forms
from .models import PieceJustificative

class PieceJustificativeForm(forms.ModelForm):
    class Meta:
        model = PieceJustificative
        fields = ['description', 'fichier']