from django.contrib import admin
from .models import Pagamento, Assinatura


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "valor", "vencimento", "pago")
    list_filter = ("pago", "vencimento")
    search_fields = ("aluno__nome",)


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ("professor", "plano", "status", "data_expiracao")
    list_filter = ("status", "plano")
    search_fields = ("professor__username", "professor__email")