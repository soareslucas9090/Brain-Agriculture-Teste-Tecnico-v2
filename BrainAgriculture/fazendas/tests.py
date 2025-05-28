from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from Common.localidades.models import Cidades, Estados
from Usuarios.produtores.models import Produtores

from .business import (
    AreaValidationService,
    CulturaBusinessService,
    FazendaBusinessService,
    SafraValidationService,
)
from .models import Culturas, Fazendas, Safras

User = get_user_model()


class AreaValidationServiceTest(TestCase):
    def test_validate_area_total_fazenda_valida(self):
        AreaValidationService.validate_area_total_fazenda(Decimal("100.50"))

    def test_validate_area_total_fazenda_zero(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_total_fazenda(Decimal("0"))

    def test_validate_area_total_fazenda_negativa(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_total_fazenda(Decimal("-10"))

    def test_validate_area_total_fazenda_muito_grande(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_total_fazenda(Decimal("200000"))

    def test_validate_area_plantada_valida(self):
        AreaValidationService.validate_area_plantada(Decimal("50.25"))

    def test_validate_area_plantada_zero(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_plantada(Decimal("0"))


class SafraValidationServiceTest(TestCase):
    def test_validate_ano_safra_valido(self):
        SafraValidationService.validate_ano_safra(2024)

    def test_validate_ano_safra_muito_antigo(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            SafraValidationService.validate_ano_safra(1800)

    def test_validate_ano_safra_muito_futuro(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            SafraValidationService.validate_ano_safra(2050)


class FazendaBusinessServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nome="Teste", cpf_cnpj="12345678901", password="testpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user, nome="Produtor Teste"
        )

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP")
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado)

        self.fazenda = Fazendas.objects.create(
            nome="Fazenda Teste",
            produtor=self.produtor,
            cidade=self.cidade,
            area_total=Decimal("1000.00"),
        )

    def test_calcular_area_info(self):
        info = FazendaBusinessService.calcular_area_info(self.fazenda, 2024)

        self.assertEqual(info["area_total"], Decimal("1000.00"))
        self.assertIn("area_agricultavel", info)
        self.assertIn("area_vegetacao", info)
        self.assertIn("percentual_agricultavel", info)
        self.assertIn("percentual_vegetacao", info)


class FazendaAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            nome="Admin", cpf_cnpj="12345678901", password="adminpass123", is_admin=True
        )

        self.user = User.objects.create_user(
            nome="Usuário", cpf_cnpj="98765432109", password="userpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user, nome="Produtor Teste"
        )
        self.user.produtor_perfil = self.produtor
        self.user.save()

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP")
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_criar_fazenda_sucesso(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Fazenda Nova",
            "produtor": self.produtor.id,
            "cidade": self.cidade.id,
            "area_total": "500.00",
        }

        response = self.client.post("/api/fazendas/fazendas/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Fazendas.objects.count(), 1)

    def test_criar_fazenda_area_invalida(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Fazenda Inválida",
            "produtor": self.produtor.id,
            "cidade": self.cidade.id,
            "area_total": "0",
        }

        response = self.client.post("/api/fazendas/fazendas/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Fazendas.objects.count(), 0)


class CulturaValidationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            nome="Teste", cpf_cnpj="12345678901", password="testpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user, nome="Produtor Teste"
        )

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP")
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado)

        self.fazenda = Fazendas.objects.create(
            nome="Fazenda Teste",
            produtor=self.produtor,
            cidade=self.cidade,
            area_total=Decimal("1000.00"),
        )

        self.safra = Safras.objects.create(fazenda=self.fazenda, ano=2024)

    def test_area_cultura_dentro_do_limite(self):
        AreaValidationService.validate_area_cultura_disponivel(
            self.safra, Decimal("500.00")
        )

    def test_area_cultura_excede_limite(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_cultura_disponivel(
                self.safra, Decimal("1500.00")
            )

    def test_area_cultura_com_outras_culturas(self):
        cultura_existente = Culturas.objects.create(
            nome="Milho", safra=self.safra, area_plantada=Decimal("600.00")
        )

        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_cultura_disponivel(
                self.safra, Decimal("500.00")
            )

    def test_area_cultura_atualizacao(self):
        cultura = Culturas.objects.create(
            nome="Soja", safra=self.safra, area_plantada=Decimal("400.00")
        )

        AreaValidationService.validate_area_cultura_disponivel(
            self.safra, Decimal("600.00"), cultura.id
        )

        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_cultura_disponivel(
                self.safra, Decimal("1200.00"), cultura.id
            )


class CulturaBusinessServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nome="Teste", cpf_cnpj="12345678901", password="testpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user, nome="Produtor Teste"
        )

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP")
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado)

        self.fazenda = Fazendas.objects.create(
            nome="Fazenda Teste",
            produtor=self.produtor,
            cidade=self.cidade,
            area_total=Decimal("1000.00"),
        )

        self.safra = Safras.objects.create(fazenda=self.fazenda, ano=2024)

        self.cultura = Culturas.objects.create(
            nome="Soja", safra=self.safra, area_plantada=Decimal("300.00")
        )

    def test_calcular_area_disponivel_cultura(self):
        info = CulturaBusinessService.calcular_area_disponivel_cultura(self.cultura)

        self.assertEqual(info["area_atual"], Decimal("300.00"))
        self.assertIn("area_agricultavel_total", info)
        self.assertIn("area_outras_culturas", info)
        self.assertIn("area_disponivel_para_expansao", info)
        self.assertIn("area_maxima_possivel", info)
        self.assertIn("percentual_utilizacao", info)

    def test_calcular_resumo_safra(self):
        resumo = CulturaBusinessService.calcular_resumo_safra(self.safra)

        self.assertIn("area_total_fazenda", resumo)
        self.assertIn("area_agricultavel", resumo)
        self.assertIn("area_vegetacao_total", resumo)
        self.assertIn("area_disponivel", resumo)
        self.assertIn("total_culturas", resumo)
        self.assertIn("percentual_utilizacao", resumo)
        self.assertIn("culturas_detalhes", resumo)

        self.assertEqual(resumo["total_culturas"], 1)
        self.assertEqual(len(resumo["culturas_detalhes"]), 1)
