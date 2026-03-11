import calendar
import json
from collections import defaultdict
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect

from alunos.models import Aluno
from aulas.models import Aula
from financeiro.models import Pagamento


def usuario_e_aluno(user):
    return Aluno.objects.filter(user=user).exists()


def inicio(request):
    return render(request, "inicio.html")


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
            messages.error(request, "Esse nome de usuário já existe.")
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

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "criar_conta.html")


@login_required
def dashboard(request):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    alunos_professor = Aluno.objects.filter(professor=request.user)

    total_alunos = alunos_professor.count()

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

    context = {
        "total_alunos": total_alunos,
        "aulas_hoje": aulas_hoje,
        "pagamentos_pagos": pagamentos_pagos,
        "pagamentos_pendentes": pagamentos_pendentes,
        "total_pendentes": total_pendentes,
        "faturamento": faturamento,
        "grafico_pagamentos": grafico_pagamentos,
        "grafico_faturamento_mensal": grafico_faturamento_mensal,
        "eh_aluno": False,
        "vapid_public_key": settings.VAPID_PUBLIC_KEY,
    }

    return render(request, "dashboard.html", context)


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
            "title": f"{aula.aluno.nome} ({aula.duracao_minutos} min)",
            "start": aula.data.isoformat(),
            "end": aula.fim.isoformat(),
        })

    return render(request, "agenda.html", {
        "eventos": eventos,
        "eh_aluno": False,
        "vapid_public_key": settings.VAPID_PUBLIC_KEY,
    })


@login_required
def painel_aluno(request):
    aluno = Aluno.objects.get(user=request.user)

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
        "vapid_public_key": settings.VAPID_PUBLIC_KEY,
    })


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

    return render(request, "novo_aluno.html", {"eh_aluno": False})


@login_required
def editar_aluno(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aluno = Aluno.objects.get(id=id, professor=request.user)

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
        "eh_aluno": False
    })


@login_required
def excluir_aluno(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aluno = Aluno.objects.get(id=id, professor=request.user)
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

        aluno = Aluno.objects.get(id=aluno_id, professor=request.user)

        Aula.objects.create(
            aluno=aluno,
            data=data,
            duracao_minutos=duracao_minutos or 50
        )

        return redirect("/agenda/")

    alunos_lista = Aluno.objects.filter(professor=request.user).order_by("nome")

    return render(request, "nova_aula.html", {
        "alunos": alunos_lista,
        "eh_aluno": False
    })


@login_required
def editar_aula(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aula = Aula.objects.get(id=id, aluno__professor=request.user)

    if request.method == "POST":
        aluno_id = request.POST.get("aluno")
        data = request.POST.get("data")
        duracao_minutos = request.POST.get("duracao_minutos")
        conteudo = request.POST.get("conteudo")

        aluno = Aluno.objects.get(id=aluno_id, professor=request.user)

        aula.aluno = aluno
        aula.data = data
        aula.duracao_minutos = duracao_minutos or 50
        aula.conteudo = conteudo

        if request.FILES.get("material"):
            aula.material = request.FILES.get("material")

        aula.save()

        return redirect("/agenda/")

    alunos_lista = Aluno.objects.filter(professor=request.user).order_by("nome")

    return render(request, "editar_aula.html", {
        "aula": aula,
        "alunos": alunos_lista,
        "eh_aluno": False
    })


@login_required
def excluir_aula(request, id):
    if usuario_e_aluno(request.user):
        return redirect("/meu-painel/")

    aula = Aula.objects.get(id=id, aluno__professor=request.user)
    aula.delete()

    return redirect("/agenda/")


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

    pagamento = Pagamento.objects.get(id=id, aluno__professor=request.user)
    pagamento.pago = True
    pagamento.save()

    return redirect("/dashboard/")




@login_required
def salvar_push_subscription(request):
    return JsonResponse({"status": "ok"})


@login_required
def push_teste(request):
    return redirect("/dashboard/")

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