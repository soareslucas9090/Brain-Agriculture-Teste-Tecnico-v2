from django.db import models
from django.utils.translation import gettext_lazy as _

from Core.BasicModel import BasicModel


class Estado(BasicModel):
    codigo_ibge = models.IntegerField(
        _("Código IBGE do Estado"),
        unique=True,
        help_text=_("Código numérico único do estado fornecido pelo IBGE."),
    )
    sigla = models.CharField(_("Sigla do Estado"), max_length=2, unique=True)

    class Meta:
        verbose_name = _("Estado")
        verbose_name_plural = _("Estados")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.sigla})"


class Cidade(BasicModel):
    codigo_ibge = models.IntegerField(
        _("Código IBGE da Cidade"),
        unique=True,
        help_text=_("Código numérico único da cidade fornecido pelo IBGE."),
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name="cidades",
        verbose_name=_("Estado"),
    )

    class Meta:
        verbose_name = _("Cidade")
        verbose_name_plural = _("Cidades")
        unique_together = ("nome", "estado")
        ordering = ["estado__nome", "nome"]

    def __str__(self):
        return f"{self.nome} - {self.estado.sigla}"
