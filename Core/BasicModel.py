import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class BasicModel(models.Model):
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Data de Criação"),
        help_text=_("Data e hora em que o registro foi criado."),
    )
    data_modificacao = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("Data de Modificação"),
        help_text=_("Data e hora da última modificação do registro."),
    )
    nome = models.CharField(
        _("Nome"),
        max_length=255,
        help_text=_("Nome do registro."),
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
        ordering = ["-data_modificacao", "-data_criacao"]
        get_latest_by = "data_criacao"

    def __str__(self):
        return str(self.nome)
