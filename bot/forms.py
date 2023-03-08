from django import forms
from . import models


class UserForm(forms.ModelForm):
    class Meta:
        model = models.UserModel
        fields = '__all__'
        widgets = {
            'foreign_id': forms.TextInput,
            'stage': forms.TextInput,
            'last_button_id': forms.TextInput
        }


class TextForm(forms.ModelForm):
    class Meta:
        model = models.TextModel
        fields = '__all__'
        widgets = {
            'button_id': forms.TextInput,
            'text': forms.Textarea
        }


class ButtonForm(forms.ModelForm):
    class Meta:
        model = models.ButtonModel
        fields = '__all__'
        widgets = {
            'from_button_id': forms.TextInput,
            'button': forms.TextInput,
            'to_button_id': forms.TextInput
        }