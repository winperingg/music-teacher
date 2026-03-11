from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

from .views import (
    inicio,
    dashboard,
    agenda,
    login_view,
    painel_aluno,
    alunos,
    novo_aluno,
    editar_aluno,
    excluir_aluno,
    nova_aula,
    editar_aula,
    excluir_aula,
    gerar_mensalidades,
    marcar_pago,
    criar_conta,
    pagamentos,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', inicio, name='inicio'),
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('meu-painel/', painel_aluno, name='painel_aluno'),

    path('agenda/', agenda, name='agenda'),

    path('alunos/', alunos, name='alunos'),
    path('alunos/novo/', novo_aluno, name='novo_aluno'),
    path('alunos/editar/<int:id>/', editar_aluno, name='editar_aluno'),
    path('alunos/excluir/<int:id>/', excluir_aluno, name='excluir_aluno'),

    path('aulas/nova/', nova_aula, name='nova_aula'),
    path('aulas/editar/<int:id>/', editar_aula, name='editar_aula'),
    path('aulas/excluir/<int:id>/', excluir_aula, name='excluir_aula'),

    path('financeiro/gerar-mensalidades/', gerar_mensalidades, name='gerar_mensalidades'),
    path('financeiro/pagar/<int:id>/', marcar_pago, name='marcar_pago'),

    path('criar-conta/', criar_conta, name='criar_conta'),

    path('pagamentos/', pagamentos, name='pagamentos'),

    path(
    'recuperar-senha/',
    auth_views.PasswordResetView.as_view(
        template_name='recuperar_senha.html'
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
        template_name='nova_senha.html'
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
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)