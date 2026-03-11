from django.contrib import admin
from django.urls import path

from .views import (
    inicio,
    login_view,
    criar_conta,
    dashboard,
    painel_aluno,
    alunos,
    novo_aluno,
    editar_aluno,
    excluir_aluno,
    agenda,
    nova_aula,
    gerar_mensalidades,
    marcar_pago,
    assinatura,
    assinar_mercadopago,
    webhook_mercadopago,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', inicio, name='inicio'),
    path('login/', login_view, name='login'),
    path('criar-conta/', criar_conta, name='criar_conta'),

    path('dashboard/', dashboard, name='dashboard'),
    path('meu-painel/', painel_aluno, name='painel_aluno'),

    path('alunos/', alunos, name='alunos'),
    path('alunos/novo/', novo_aluno, name='novo_aluno'),
    path('alunos/editar/<int:id>/', editar_aluno, name='editar_aluno'),
    path('alunos/excluir/<int:id>/', excluir_aluno, name='excluir_aluno'),

    path('agenda/', agenda, name='agenda'),
    path('aulas/nova/', nova_aula, name='nova_aula'),

    path('financeiro/gerar-mensalidades/', gerar_mensalidades, name='gerar_mensalidades'),
    path('financeiro/pagar/<int:id>/', marcar_pago, name='marcar_pago'),

    path('assinatura/', assinatura, name='assinatura'),

    path('assinatura/', assinatura, name='assinatura'),
path('assinar/mercadopago/', assinar_mercadopago, name='assinar_mercadopago'),
path('webhooks/mercadopago/', webhook_mercadopago, name='webhook_mercadopago'),
]