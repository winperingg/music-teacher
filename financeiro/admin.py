from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Pagamento

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "valor", "vencimento", "pago")
    list_filter = ("pago",)