from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    inicio,
    login_view,
    criar_conta,
    dashboard,
    agenda,
    painel_aluno,
    alunos,
    novo_aluno,
    editar_aluno,
    excluir_aluno,
    nova_aula,
    editar_aula,
    excluir_aula,
    pagamentos,
    gerar_mensalidades,
    marcar_pago,
    assinatura,
    assinar_mercadopago,
    webhook_mercadopago,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    # PAGINA INICIAL
    path('', inicio, name='inicio'),

    # LOGIN / CONTA
    path('login/', login_view, name='login'),
    path('criar-conta/', criar_conta, name='criar_conta'),

    # RECUPERAR SENHA
  path(
    'recuperar-senha/',
    auth_views.PasswordResetView.as_view(
        template_name='recuperar_senha.html',
        email_template_name='emails/password_reset_email.html',
        subject_template_name='emails/password_reset_subject.txt',
        success_url='/senha-enviada/'
    ),
    name='password_reset'
),

path(
    'senha-enviada/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='senha_enviada.html'
    ),
    name='password_reset_done'
),

path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='nova_senha.html',
        success_url='/senha-resetada/'
    ),
    name='password_reset_confirm'
),

path(
    'senha-resetada/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='senha_resetada.html'
    ),
    name='password_reset_complete'
),

    # PAINEL ALUNO
    path('meu-painel/', painel_aluno, name='painel_aluno'),

    # AGENDA
    path('agenda/', agenda, name='agenda'),

    # ALUNOS
    path('alunos/', alunos, name='alunos'),
    path('alunos/novo/', novo_aluno, name='novo_aluno'),
    path('alunos/editar/<int:id>/', editar_aluno, name='editar_aluno'),
    path('alunos/excluir/<int:id>/', excluir_aluno, name='excluir_aluno'),

    # AULAS
    path('aulas/nova/', nova_aula, name='nova_aula'),
    path('aulas/editar/<int:id>/', editar_aula, name='editar_aula'),
    path('aulas/excluir/<int:id>/', excluir_aula, name='excluir_aula'),

    # PAGAMENTOS
    path('pagamentos/', pagamentos, name='pagamentos'),
    path('financeiro/gerar-mensalidades/', gerar_mensalidades, name='gerar_mensalidades'),
    path('financeiro/pagar/<int:id>/', marcar_pago, name='marcar_pago'),

    # ASSINATURA
    path('assinatura/', assinatura, name='assinatura'),
    path('assinar/', assinar_mercadopago, name='assinar_mercadopago'),

    # WEBHOOK MERCADO PAGO
    path('webhook/mercadopago/', webhook_mercadopago, name='webhook_mercadopago'),
    path('dashboard/', dashboard, name='dashboard'),
]
