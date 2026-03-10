from django.contrib import admin
from .models import Aula


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ("aluno", "data", "duracao_minutos", "realizada")
    list_filter = ("realizada",)