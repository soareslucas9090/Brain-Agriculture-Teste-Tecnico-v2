from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from Core.BasicModel import BasicModel
from Core.Validations import validar_cpf_cnpj


class UsuariosManager(BaseUserManager):
    def _create_user(self, cpf_cnpj, password, **extra_fields):
        if not cpf_cnpj:
            raise ValueError(_("O CPF/CNPJ deve ser fornecido."))

        cpf_cnpj = "".join(filter(str.isdigit, cpf_cnpj))

        user = self.model(cpf_cnpj=cpf_cnpj, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, cpf_cnpj, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(cpf_cnpj, password, **extra_fields)

    def create_superuser(self, cpf_cnpj, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_admin") is not True:
            raise ValueError(_("Superusuário deve ter is_admin=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superusuário deve ter is_superuser=True."))

        return self._create_user(cpf_cnpj, password, **extra_fields)


class Usuarios(AbstractBaseUser, BasicModel):
    cpf_cnpj = models.CharField(
        _("CPF/CNPJ"),
        max_length=14,
        unique=True,
        help_text=_("Obrigatório. CPF ou CNPJ único para login."),
        error_messages={
            "unique": _("Já existe um usuário cadastrado com este CPF/CNPJ."),
        },
    )

    is_active = models.BooleanField(
        _("Ativo"),
        default=True,
        help_text=_(
            "Define o status de atividade do usuário. "
            "Desmarque esta opção em vez de excluir contas."
        ),
    )
    is_superuser = models.BooleanField(
        _("Superusuário"),
        default=False,
        help_text=_(
            "Designa se o usuário pode fazer login no site de administração (admin)."
        ),
    )
    is_admin = models.BooleanField(
        _("Administrador do Sistema"),
        default=False,
        help_text=_(
            "Designa se o usuário tem privilégios de administrador no sistema. "
            "Se True, o usuário terá todas as permissões (is_superuser) e acesso ao admin (is_staff)."
        ),
    )
    last_login = None

    objects = UsuariosManager()

    USERNAME_FIELD = "cpf_cnpj"
    REQUIRED_FIELDS = [
        "nome",
    ]

    class Meta:
        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")

    def __str__(self):
        return f"{self.cpf_cnpj} - {self.nome}"

    def capitalizar_nome(self):
        nome_capitalizado = []
        preposicoes = ["da", "de", "do"]

        for nome in self.nome.split():
            if not nome in preposicoes:
                nome = nome.capitalize()
            nome_capitalizado.append(nome)

        novo_nome = " ".join(nome_capitalizado)
        self.nome = novo_nome

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_admin = True

        validar_cpf_cnpj(self.cpf_cnpj)

        self.capitalizar_nome()

        super().save(*args, **kwargs)
