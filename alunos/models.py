from django.db import models
from django.contrib.auth.models import User

class Aluno(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alunos")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    instrumento = models.CharField(max_length=100)
    valor_mensalidade = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    dia_vencimento = models.IntegerField(default=10)
    data_cadastro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome