from django.db import models
from django.utils.translation import gettext_lazy as _

from Common.localidades.models import Cidades
from Core.BasicModel import BasicModel
from Usuarios.produtores.models import Produtores


class Fazendas(BasicModel):
    produtor = models.ForeignKey(
        Produtores,
        on_delete=models.PROTECT,
        related_name="fazendas",
        verbose_name=_("Proprietário da fazenda."),
        help_text=_("O usuário/produtor quer será associado à fazenda."),
    )
    cidade = models.ForeignKey(
        Cidades,
        on_delete=models.PROTECT,
        related_name="fazendas",
        verbose_name=_("Localização da fazenda."),
        help_text=_("A cidade onde a fazenda está localizada."),
    )
    area_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Área total da fazenda, em hectares."),
    )

    def __str__(self):
        return f"{self.nome} - {self.produtor.usuario.nome}"

    class Meta:
        verbose_name = _("Fazenda")
        verbose_name_plural = _("Fazendas")
        unique_together = [["nome", "produtor"]]
        ordering = ["nome"]

    def area_agricultavel(self, ano_referencia):
        return self.area_total - self.area_vegetacao(ano_referencia)

    def area_vegetacao(self, ano_referencia):
        return sum(
            safra.area_vegetacao_total
            for safra in self.safras.filter(ano=ano_referencia)
        )


class Safras(BasicModel):
    fazenda = models.ForeignKey(
        Fazendas,
        on_delete=models.CASCADE,
        related_name="safras",
        verbose_name=_("Fazenda"),
        help_text=_("A fazenda relacionada à safra."),
    )
    ano = models.IntegerField(
        verbose_name=_("Ano"),
        help_text=_("Ano da safra."),
    )

    def save(self, *args, **kwargs):
        self.nome = f"Safra de {self.ano}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Safra")
        verbose_name_plural = _("Safras")
        ordering = ["-ano"]

    @property
    def area_vegetacao_total(self):
        return sum(cultura.area_plantada for cultura in self.culturas.all())


class Culturas(BasicModel):
    safra = models.ForeignKey(
        Safras,
        verbose_name=_("Safra"),
        on_delete=models.PROTECT,
        related_name="culturas",
        help_text=_("A safra relacionada à cultura."),
    )
    area_plantada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Área plantada da cultura, em hectares."),
    )

    def __str__(self):
        return f"{self.nome} - {self.safra}"

    class Meta:
        verbose_name = _("Cultura")
        verbose_name_plural = _("Culturas")
        ordering = ["safra__ano", "nome"]
