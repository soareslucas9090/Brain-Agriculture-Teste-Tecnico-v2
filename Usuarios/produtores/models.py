from django.db import models


class Produtor(BasicModel):
    usuario = models.OneToOneField(
        "Usuarios.usuarios",
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
