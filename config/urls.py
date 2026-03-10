from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

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
    salvar_push_subscription,
    push_teste,
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

    path('push/subscribe/', salvar_push_subscription, name='salvar_push_subscription'),
    path('push/teste/', push_teste, name='push_teste'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)