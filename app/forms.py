from django import forms
from .models import DifyModel


class DifyForm(forms.ModelForm):
    class Meta:
        model = DifyModel
        fields = ['query']