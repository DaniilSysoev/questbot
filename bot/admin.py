from django.contrib import admin
from . import models
from . import forms


@admin.register(models.UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('foreign_id', 'stage', 'last_button_id')
    form = forms.UserForm


@admin.register(models.TextModel)
class TextAdmin(admin.ModelAdmin):
    list_display = ('button_id', 'text')
    form = forms.TextForm


@admin.register(models.ButtonModel)
class ButtonAdmin(admin.ModelAdmin):
    list_display = ('from_button_id', 'button', 'to_button_id')
    form = forms.ButtonForm


@admin.register(models.PlotModel)
class PlotAdmin(admin.ModelAdmin):
    list_display = ['link']
    form = forms.PlotForm