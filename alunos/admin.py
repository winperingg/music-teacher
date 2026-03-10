from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Aluno


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "email", "instrumento", "data_cadastro")
    search_fields = ("nome", "telefone", "email")