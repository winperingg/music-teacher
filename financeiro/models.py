from django.db import models
from alunos.models import Aluno


class Pagamento(models.Model):

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)

    valor = models.DecimalField(max_digits=8, decimal_places=2)

    vencimento = models.DateField()

    pago = models.BooleanField(default=False)

    data_pagamento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.aluno.nome} - {self.valor}"