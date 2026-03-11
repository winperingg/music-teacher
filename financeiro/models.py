from django.db import models
from django.contrib.auth.models import User


class Pagamento(models.Model):
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    vencimento = models.DateField()
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.aluno.nome} - {self.valor}"


class Assinatura(models.Model):
    STATUS_CHOICES = [
        ("trial", "Trial"),
        ("pendente", "Pendente"),
        ("ativa", "Ativa"),
        ("cancelada", "Cancelada"),
        ("expirada", "Expirada"),
    ]

    professor = models.OneToOneField(User, on_delete=models.CASCADE)
    plano = models.CharField(max_length=50, default="mensal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trial")
    data_inicio = models.DateField(auto_now_add=True)
    data_expiracao = models.DateField(null=True, blank=True)

    mp_preapproval_id = models.CharField(max_length=120, blank=True, null=True)
    mp_init_point = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.professor.username} - {self.status}"