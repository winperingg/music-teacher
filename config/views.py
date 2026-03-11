import calendar
from collections import defaultdict
from datetime import date, timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from alunos.models import Aluno
from aulas.models import Aula
from financeiro.models import Assinatura, Pagamento


# -------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------

def usuario_e_aluno(user):
    return Aluno.objects.filter(user=user).exists()


def assinatura_valida(user):
    try:
        assinatura = Assinatura.objects.get(professor=user)
        return assinatura.status == "ativa"
    except Assinatura.DoesNotExist:
        return False


def criar_assinatura_mercadopago(payer_email, external_reference):
    url = "https://api.mercadopago.com/preapproval"

    headers = {
        "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "preapproval_plan_id": settings.MERCADOPAGO_PLAN_ID,
        "reason": "Assinatura Music Teacher",
        "payer_email": payer_email,
        "external_reference": str(external_reference),
        "back_url": f"{settings.SITE_URL}/assinatura/",
        "status": "pending",
    }

    response = requests.post(url, json=data, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def consultar_assinatura_mercadopago(preapproval_id):
    url = f"https://api.mercadopago.com/preapproval/{preapproval_id}"

    headers = {
        "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


# -------------------------------
# PÁGINA INICIAL
# -------------------------------

def inicio(request):
    return render(request, "inicio.html")


# -------------------------------
# LOGIN
# -------------------------------

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

        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "login.html")


# -------------------------------
# CRIAR CONTA PROFESSOR
# -------------------------------

def criar_conta(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmar = request.POST.get("confirmar")

        if password != confirmar:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "criar_conta.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe.")
            return render(request, "criar_conta.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Esse e-mail já está cadastrado.")
            return render(request, "criar_conta.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nome
        )

        Assinatura.objects.create(
            professor=user,
            plano="mensal",
            status="trial",
            data_expiracao=date.today() + timedelta(days=7)
        )

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "criar_conta.html")


# -------------------------------
# DASHBOARD PROFESSOR
# -------------------------------

@login_required
def dashboard(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    if not assinatura_valida(request.user):
        return redirect("/assinatura/")

    total_alunos = Aluno.objects.filter(professor=request.user).count()

    aulas_hoje = Aula.objects.filter(
        aluno__professor=request.user,
        data__date=date.today()
    ).order_by("data")

    pagamentos_pagos = Pagamento.objects.filter(
        aluno__professor=request.user,
        pago=True
    ).count()

    pagamentos_pendentes = Pagamento.objects.filter(
        aluno__professor=request.user,
        pago=False
    ).order_by("vencimento")

    total_pendentes = pagamentos_pendentes.count()

    faturamento = Pagamento.objects.filter(
        aluno__professor=request.user,
        pago=True
    ).aggregate(total=Sum("valor"))["total"] or 0

    grafico_pagamentos = {
        "labels": ["Pagos", "Pendentes"],
        "valores": [pagamentos_pagos, total_pendentes],
    }

    pagamentos_por_mes = Pagamento.objects.filter(
        aluno__professor=request.user,
        pago=True
    ).order_by("vencimento")

    meses = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez"
    ]

    faturamento_mensal_map = defaultdict(float)

    for pagamento in pagamentos_por_mes:
        mes_nome = meses[pagamento.vencimento.month - 1]
        faturamento_mensal_map[mes_nome] += float(pagamento.valor)

    grafico_faturamento_mensal = {
        "labels": list(faturamento_mensal_map.keys()),
        "valores": list(faturamento_mensal_map.values()),
    }

    return render(request, "dashboard.html", {
        "total_alunos": total_alunos,
        "aulas_hoje": aulas_hoje,
        "pagamentos_pagos": pagamentos_pagos,
        "pagamentos_pendentes": pagamentos_pendentes,
        "total_pendentes": total_pendentes,
        "faturamento": faturamento,
        "grafico_pagamentos": grafico_pagamentos,
        "grafico_faturamento_mensal": grafico_faturamento_mensal,
        "eh_aluno": False,
    })


# -------------------------------
# PAINEL DO ALUNO
# -------------------------------

@login_required
def painel_aluno(request):
    aluno = get_object_or_404(Aluno, user=request.user)

    aulas = Aula.objects.filter(aluno=aluno).order_by("data")

    proxima_aula = Aula.objects.filter(
        aluno=aluno,
        data__date__gte=date.today()
    ).order_by("data").first()

    return render(request, "painel_aluno.html", {
        "aluno": aluno,
        "aulas": aulas,
        "proxima_aula": proxima_aula,
        "eh_aluno": True,
    })


# -------------------------------
# ALUNOS
# -------------------------------

@login_required
def alunos(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    lista_alunos = Aluno.objects.filter(professor=request.user).order_by("nome")

    return render(request, "alunos.html", {
        "alunos": lista_alunos,
        "eh_aluno": False,
    })


@login_required
def novo_aluno(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        instrumento = request.POST.get("instrumento")
        valor_mensalidade = request.POST.get("valor_mensalidade")
        dia_vencimento = request.POST.get("dia_vencimento")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not nome:
            messages.error(request, "Informe o nome do aluno.")
            return render(request, "novo_aluno.html", {"eh_aluno": False})

        if username and User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe.")
            return render(request, "novo_aluno.html", {"eh_aluno": False})

        user = None
        if username and password:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email or ""
            )

        Aluno.objects.create(
            professor=request.user,
            user=user,
            nome=nome,
            telefone=telefone or "",
            email=email or "",
            instrumento=instrumento or "",
            valor_mensalidade=valor_mensalidade or 0,
            dia_vencimento=dia_vencimento or 10,
        )

        messages.success(request, "Aluno cadastrado com sucesso.")
        return redirect("/alunos/")

    return render(request, "novo_aluno.html", {
        "eh_aluno": False
    })


@login_required
def editar_aluno(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aluno = get_object_or_404(Aluno, id=id, professor=request.user)

    if request.method == "POST":
        aluno.nome = request.POST.get("nome")
        aluno.telefone = request.POST.get("telefone")
        aluno.email = request.POST.get("email")
        aluno.instrumento = request.POST.get("instrumento")
        aluno.valor_mensalidade = request.POST.get("valor_mensalidade") or 0
        aluno.dia_vencimento = request.POST.get("dia_vencimento") or 10
        aluno.save()

        return redirect("/alunos/")

    return render(request, "editar_aluno.html", {
        "aluno": aluno,
        "eh_aluno": False,
    })


@login_required
def excluir_aluno(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aluno = get_object_or_404(Aluno, id=id, professor=request.user)
    aluno.delete()

    return redirect("/alunos/")


# -------------------------------
# AGENDA / AULAS
# -------------------------------

@login_required
def agenda(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aulas = Aula.objects.filter(
        aluno__professor=request.user
    ).order_by("data")

    eventos = []
    for aula in aulas:
        eventos.append({
            "id": aula.id,
            "title": f"{aula.aluno.nome} ({getattr(aula, 'duracao_minutos', 50)} min)",
            "start": aula.data.isoformat(),
            "end": aula.fim.isoformat() if hasattr(aula, "fim") else aula.data.isoformat(),
        })

    return render(request, "agenda.html", {
        "eventos": eventos,
        "eh_aluno": False,
    })


@login_required
def nova_aula(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    if request.method == "POST":
        aluno_id = request.POST.get("aluno")
        data = request.POST.get("data")
        duracao_minutos = request.POST.get("duracao_minutos")

        aluno = get_object_or_404(Aluno, id=aluno_id, professor=request.user)

        Aula.objects.create(
            aluno=aluno,
            data=data,
            duracao_minutos=duracao_minutos or 50
        )

        return redirect("/agenda/")

    alunos_lista = Aluno.objects.filter(professor=request.user).order_by("nome")

    return render(request, "nova_aula.html", {
        "alunos": alunos_lista,
        "eh_aluno": False,
    })


@login_required
def editar_aula(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aula = get_object_or_404(Aula, id=id, aluno__professor=request.user)

    if request.method == "POST":
        aluno_id = request.POST.get("aluno")
        data = request.POST.get("data")
        duracao_minutos = request.POST.get("duracao_minutos")
        conteudo = request.POST.get("conteudo")

        aluno = get_object_or_404(Aluno, id=aluno_id, professor=request.user)

        aula.aluno = aluno
        aula.data = data
        aula.duracao_minutos = duracao_minutos or 50
        aula.conteudo = conteudo or ""

        if request.FILES.get("material"):
            aula.material = request.FILES.get("material")

        aula.save()

        return redirect("/agenda/")

    alunos_lista = Aluno.objects.filter(professor=request.user).order_by("nome")

    return render(request, "editar_aula.html", {
        "aula": aula,
        "alunos": alunos_lista,
        "eh_aluno": False,
    })


@login_required
def excluir_aula(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aula = get_object_or_404(Aula, id=id, aluno__professor=request.user)
    aula.delete()

    return redirect("/agenda/")


# -------------------------------
# PAGAMENTOS
# -------------------------------

@login_required
def pagamentos(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    mes = request.GET.get("mes")

    pagamentos_lista = Pagamento.objects.filter(
        aluno__professor=request.user
    ).order_by("vencimento")

    if mes:
        pagamentos_lista = pagamentos_lista.filter(vencimento__month=mes)

    return render(request, "pagamentos.html", {
        "pagamentos": pagamentos_lista,
        "eh_aluno": False,
        "mes_selecionado": mes,
    })


@login_required
def gerar_mensalidades(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    hoje = date.today()
    ano = hoje.year
    mes = hoje.month

    alunos_lista = Aluno.objects.filter(professor=request.user)

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

    return redirect("/dashboard/")


@login_required
def marcar_pago(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    pagamento = get_object_or_404(
        Pagamento,
        id=id,
        aluno__professor=request.user
    )
    pagamento.pago = True
    pagamento.save()

    return redirect("/dashboard/")


# -------------------------------
# ASSINATURA
# -------------------------------

@login_required
def assinatura(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    assinatura_obj, criada = Assinatura.objects.get_or_create(
        professor=request.user,
        defaults={
            "plano": "mensal",
            "status": "trial",
            "data_expiracao": date.today() + timedelta(days=7)
        }
    )

    return render(request, "assinatura.html", {
        "assinatura": assinatura_obj,
        "eh_aluno": False,
    })


@login_required
def assinar_mercadopago(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    assinatura_obj, criada = Assinatura.objects.get_or_create(
        professor=request.user,
        defaults={
            "plano": "mensal",
            "status": "trial",
            "data_expiracao": date.today() + timedelta(days=7)
        }
    )

    if not request.user.email:
        messages.error(request, "Adicione um e-mail na sua conta antes de assinar.")
        return redirect("/assinatura/")

    try:
        resultado = criar_assinatura_mercadopago(
            payer_email=request.user.email,
            external_reference=request.user.id
        )

        assinatura_obj.status = "pendente"
        assinatura_obj.mp_preapproval_id = resultado.get("id")
        assinatura_obj.mp_init_point = resultado.get("init_point")
        assinatura_obj.save()

        init_point = resultado.get("init_point")

        if init_point:
            return redirect(init_point)

        messages.error(request, "Não foi possível iniciar a assinatura.")
        return redirect("/assinatura/")

    except Exception:
        messages.error(request, "Erro ao conectar com o Mercado Pago.")
        return redirect("/assinatura/")


@csrf_exempt
def webhook_mercadopago(request):
    if request.method != "POST":
        return HttpResponse(status=200)

    topic = request.GET.get("topic") or request.GET.get("type")
    preapproval_id = request.GET.get("id")

    if not preapproval_id:
        return HttpResponse(status=200)

    try:
        dados = consultar_assinatura_mercadopago(preapproval_id)
    except Exception:
        return HttpResponse(status=200)

    external_reference = dados.get("external_reference")
    mp_status = dados.get("status")

    if not external_reference:
        return HttpResponse(status=200)

    try:
        assinatura_obj = Assinatura.objects.get(professor_id=int(external_reference))
    except Assinatura.DoesNotExist:
        return HttpResponse(status=200)

    assinatura_obj.mp_preapproval_id = dados.get("id", assinatura_obj.mp_preapproval_id)

    if mp_status == "authorized":
        assinatura_obj.status = "ativa"
    elif mp_status in ["paused", "cancelled"]:
        assinatura_obj.status = "cancelada"
    elif mp_status == "pending":
        assinatura_obj.status = "pendente"

    assinatura_obj.save()

    return HttpResponse(status=200)