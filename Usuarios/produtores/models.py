from django.db import models
from django.utils.translation import gettext_lazy as _

from Core.BasicModel import BasicModel
from Usuarios.usuarios.models import Usuarios


class Produtores(BasicModel):
    usuario = models.OneToOneField(
        Usuarios,
        on_delete=models.CASCADE,
        related_name="produtor_perfil",
        verbose_name=_("Usuário do Sistema"),
        help_text=_("O usuário do sistema associado a este perfil de produtor."),
    )

    def __str__(self):
        return self.nome_produtor

    class Meta:
        verbose_name = _("Produtor Rural")
        verbose_name_plural = _("Produtores Rurais")
