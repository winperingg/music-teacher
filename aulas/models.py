from django.db import models
from alunos.models import Aluno
from datetime import timedelta

class Aula(models.Model):

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)

    data = models.DateTimeField()

    duracao_minutos = models.IntegerField(default=50)

    conteudo = models.TextField(blank=True)

    material = models.FileField(upload_to="materiais/", blank=True, null=True)

    realizada = models.BooleanField(default=False)

    @property
    def fim(self):
        return self.data + timedelta(minutes=self.duracao_minutos)

    def __str__(self):
        return f"{self.aluno.nome} - {self.data}"