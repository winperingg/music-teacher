import json
from django.http import JsonResponse
from django.conf import settings
from pywebpush import webpush
from alunos.models import PushSubscription
import calendar
from collections import defaultdict
from datetime import date

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render, redirect

from alunos.models import Aluno
from aulas.models import Aula
from financeiro.models import Pagamento


def usuario_e_aluno(user):
    return Aluno.objects.filter(user=user).exists()


@login_required
def dashboard(request):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    total_alunos = Aluno.objects.count()
    aulas_hoje = Aula.objects.filter(data__date=date.today())

    pagamentos_pagos = Pagamento.objects.filter(pago=True).count()
    pagamentos_pendentes = Pagamento.objects.filter(pago=False)
    total_pendentes = pagamentos_pendentes.count()

    faturamento = Pagamento.objects.filter(pago=True).aggregate(
        total=Sum("valor")
    )["total"] or 0

    grafico_pagamentos = {
        "labels": ["Pagos", "Pendentes"],
        "valores": [pagamentos_pagos, total_pendentes],
    }

    pagamentos_por_mes = Pagamento.objects.filter(pago=True).order_by("vencimento")

    meses = [
        "Jan","Fev","Mar","Abr","Mai","Jun",
        "Jul","Ago","Set","Out","Nov","Dez"
    ]

    faturamento_mensal_map = defaultdict(float)

    for pagamento in pagamentos_por_mes:
        mes_nome = meses[pagamento.vencimento.month - 1]
        faturamento_mensal_map[mes_nome] += float(pagamento.valor)

    grafico_faturamento_mensal = {
        "labels": list(faturamento_mensal_map.keys()),
        "valores": list(faturamento_mensal_map.values()),
    }

    context = {
        "total_alunos": total_alunos,
        "aulas_hoje": aulas_hoje,
        "pagamentos_pagos": pagamentos_pagos,
        "pagamentos_pendentes": pagamentos_pendentes,
        "total_pendentes": total_pendentes,
        "faturamento": faturamento,
        "grafico_pagamentos": grafico_pagamentos,
        "grafico_faturamento_mensal": grafico_faturamento_mensal,
        "eh_aluno": False
    }

    return render(request, "dashboard.html", context)


@login_required
def agenda(request):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aulas = Aula.objects.all()

    eventos = []
    for aula in aulas:
        eventos.append({
            "id": aula.id,
            "title": f"{aula.aluno.nome} ({aula.duracao_minutos} min)",
            "start": aula.data.isoformat(),
            "end": aula.fim.isoformat(),
        })

    return render(request, "agenda.html", {
        "eventos": eventos,
        "eh_aluno": False
    })


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if usuario_e_aluno(user):
                return redirect("/meu-painel/")

            return redirect("/dashboard/")

    return render(request, "login.html")


@login_required
def painel_aluno(request):

    aluno = Aluno.objects.get(user=request.user)

    aulas = Aula.objects.filter(aluno=aluno).order_by("data")

    proxima_aula = Aula.objects.filter(
        aluno=aluno,
        data__gte=date.today()
    ).order_by("data").first()

    return render(request, "painel_aluno.html", {
    "aluno": aluno,
    "aulas": aulas,
    "proxima_aula": proxima_aula,
    "eh_aluno": True,

})

@login_required
def alunos(request):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    lista_alunos = Aluno.objects.all()

    return render(request, "alunos.html", {
        "alunos": lista_alunos,
        "eh_aluno": False
    })


@login_required
def novo_aluno(request):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    erro = None

    if request.method == "POST":

        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        instrumento = request.POST.get("instrumento")
        valor_mensalidade = request.POST.get("valor_mensalidade")
        dia_vencimento = request.POST.get("dia_vencimento")

        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            erro = "Esse nome de usuário já existe."

        else:

            user = User.objects.create_user(
                username=username,
                password=password
            )

            Aluno.objects.create(
                user=user,
                nome=nome,
                telefone=telefone,
                email=email,
                instrumento=instrumento,
                valor_mensalidade=valor_mensalidade,
                dia_vencimento=dia_vencimento
            )

            return redirect("/alunos/")

    return render(request, "novo_aluno.html", {
        "erro": erro,
        "eh_aluno": False
    })


@login_required
def editar_aluno(request, id):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aluno = Aluno.objects.get(id=id)

    if request.method == "POST":

        aluno.nome = request.POST.get("nome")
        aluno.telefone = request.POST.get("telefone")
        aluno.email = request.POST.get("email")
        aluno.instrumento = request.POST.get("instrumento")

        aluno.save()

        return redirect("/alunos/")

    return render(request, "editar_aluno.html", {
        "aluno": aluno,
        "eh_aluno": False
    })


@login_required
def excluir_aluno(request, id):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aluno = Aluno.objects.get(id=id)
    aluno.delete()

    return redirect("/alunos/")


@login_required
def nova_aula(request):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    if request.method == "POST":

        aluno_id = request.POST.get("aluno")
        data = request.POST.get("data")
        duracao_minutos = request.POST.get("duracao_minutos")

        Aula.objects.create(
            aluno_id=aluno_id,
            data=data,
            duracao_minutos=duracao_minutos
        )

        return redirect("/agenda/")

    alunos_lista = Aluno.objects.all()

    return render(request, "nova_aula.html", {
        "alunos": alunos_lista,
        "eh_aluno": False
    })


@login_required
def editar_aula(request, id):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aula = Aula.objects.get(id=id)

    if request.method == "POST":

        aluno_id = request.POST.get("aluno")
        data = request.POST.get("data")
        duracao_minutos = request.POST.get("duracao_minutos")
        conteudo = request.POST.get("conteudo")

        aula.aluno_id = aluno_id
        aula.data = data
        aula.duracao_minutos = duracao_minutos
        aula.conteudo = conteudo

        if request.FILES.get("material"):
            aula.material = request.FILES.get("material")

        aula.save()

        return redirect("/agenda/")

    alunos_lista = Aluno.objects.all()

    return render(request, "editar_aula.html", {
        "aula": aula,
        "alunos": alunos_lista,
        "eh_aluno": False
    })


@login_required
def excluir_aula(request, id):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aula = Aula.objects.get(id=id)
    aula.delete()

    return redirect("/agenda/")


@login_required
def gerar_mensalidades(request):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    hoje = date.today()
    ano = hoje.year
    mes = hoje.month

    alunos_lista = Aluno.objects.all()

    for aluno in alunos_lista:

        ultimo_dia = calendar.monthrange(ano, mes)[1]

        dia_vencimento = min(aluno.dia_vencimento, ultimo_dia)

        vencimento = date(ano, mes, dia_vencimento)

        existe = Pagamento.objects.filter(
            aluno=aluno,
            vencimento__year=ano,
            vencimento__month=mes
        ).exists()

        if not existe:

            Pagamento.objects.create(
                aluno=aluno,
                valor=aluno.valor_mensalidade,
                vencimento=vencimento,
                pago=False
            )

    return redirect("/")


@login_required
def marcar_pago(request, id):

    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    pagamento = Pagamento.objects.get(id=id)

    pagamento.pago = True
    pagamento.save()

    return redirect("/")
def inicio(request):
    return render(request, "inicio.html")
@login_required
def salvar_push_subscription(request):
    if request.method == "POST":
        data = json.loads(request.body)

        endpoint = data["endpoint"]
        p256dh = data["keys"]["p256dh"]
        auth = data["keys"]["auth"]

        PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={
                "p256dh": p256dh,
                "auth": auth,
            }
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "erro"}, status=400)


@login_required
def push_teste(request):
    subscriptions = PushSubscription.objects.filter(user=request.user)

    for sub in subscriptions:
        webpush(
            subscription_info={
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth,
                },
            },
            data=json.dumps({
                "title": "Teste de notificação 🎸",
                "body": "Push funcionando no seu sistema."
            }),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": settings.VAPID_ADMIN_EMAIL,
            }
        )

    return redirect("/dashboard/")