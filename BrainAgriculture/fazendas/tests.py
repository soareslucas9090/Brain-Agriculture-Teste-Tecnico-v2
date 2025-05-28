from decimal import Decimal
from datetime import datetime

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
    
    def test_validate_area_plantada_negativa(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            AreaValidationService.validate_area_plantada(Decimal("-10"))
    
    def test_validate_area_total_fazenda_valida(self):
        AreaValidationService.validate_area_total_fazenda(Decimal("100.50"))


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
    
    def test_validate_safra_unica_por_fazenda_ano(self):
        from rest_framework import serializers
        
        user = User.objects.create_user(
            nome="Teste", cpf_cnpj="66484750050", password="testpass123"
        )
        produtor = Produtores.objects.create(usuario=user)
        estado = Estados.objects.create(nome="SP", sigla="SP", codigo_ibge=1)
        cidade = Cidades.objects.create(nome="São Paulo", estado=estado, codigo_ibge=1)
        fazenda = Fazendas.objects.create(
            nome="Fazenda", produtor=produtor, cidade=cidade, area_total=Decimal("100")
        )
        Safras.objects.create(fazenda=fazenda, ano=2024)
        
        with self.assertRaises(serializers.ValidationError):
            SafraValidationService.validate_safra_unica_por_fazenda_ano(fazenda, 2024)


class FazendaBusinessServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nome="Teste", cpf_cnpj="10818104082", password="testpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user
        )

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP", codigo_ibge=1)
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado, codigo_ibge=2)

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
    
    def test_calcular_area_info_com_safra(self):
        safra = Safras.objects.create(fazenda=self.fazenda, ano=2024)
        Culturas.objects.create(nome="Soja", safra=safra, area_plantada=Decimal("300"))
        
        info = FazendaBusinessService.calcular_area_info(self.fazenda, 2024)
        
        self.assertEqual(info["area_total"], Decimal("1000.00"))
        self.assertEqual(info["area_vegetacao"], Decimal("300.00"))


class FazendaAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            nome="Admin", cpf_cnpj="35301408054", password="adminpass123", is_admin=True
        )

        self.user = User.objects.create_user(
            nome="Usuário", cpf_cnpj="99193226012", password="userpass123"
        )
        
        self.user2 = User.objects.create_user(
            nome="Usuário 2", cpf_cnpj="22765069034", password="userpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user
        )
        self.user.produtor_perfil = self.produtor
        self.user.save()
        
        self.produtor2 = Produtores.objects.create(
            usuario=self.user2
        )
        self.user2.produtor_perfil = self.produtor2
        self.user2.save()

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP", codigo_ibge=3)
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado, codigo_ibge=4)
        self.cidade2 = Cidades.objects.create(nome="São Paulo", estado=self.estado, codigo_ibge=5)

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

        response = self.client.post("/api/brainagriculture/v1/fazendas/", data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Fazendas.objects.count(), 1)
        self.assertEqual(response.data["nome"], "Fazenda Nova")

    def test_criar_fazenda_area_invalida(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Fazenda Inválida",
            "produtor": self.produtor.id,
            "cidade": self.cidade.id,
            "area_total": "0",
        }

        response = self.client.post("/api/brainagriculture/v1/fazendas/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Fazendas.objects.count(), 0)
    
    def test_criar_fazenda_produtor_outro_usuario(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Fazenda Outro",
            "produtor": self.produtor2.id,
            "cidade": self.cidade.id,
            "area_total": "500.00",
        }

        response = self.client.post("/api/brainagriculture/v1/fazendas/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_listar_fazendas_produtor(self):
        Fazendas.objects.create(
            nome="Fazenda 1", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("100")
        )
        Fazendas.objects.create(
            nome="Fazenda 2", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("200")
        )
        Fazendas.objects.create(
            nome="Fazenda Outro", produtor=self.produtor2, cidade=self.cidade, area_total=Decimal("300")
        )
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get("/api/brainagriculture/v1/fazendas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_listar_fazendas_admin(self):
        Fazendas.objects.create(
            nome="Fazenda 1", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("100")
        )
        Fazendas.objects.create(
            nome="Fazenda 2", produtor=self.produtor2, cidade=self.cidade, area_total=Decimal("200")
        )
        
        token = self.get_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get("/api/brainagriculture/v1/fazendas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_filtrar_fazendas(self):
        fazenda1 = Fazendas.objects.create(
            nome="Fazenda A", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("100")
        )
        fazenda2 = Fazendas.objects.create(
            nome="Fazenda B", produtor=self.produtor, cidade=self.cidade2, area_total=Decimal("200")
        )
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/fazendas/?nome=Fazenda A")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["nome"], "Fazenda A")
        
        response = self.client.get(f"/api/brainagriculture/v1/fazendas/?cidade={self.cidade2.id}")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["nome"], "Fazenda B")
        
        response = self.client.get(f"/api/brainagriculture/v1/fazendas/?produtor={self.produtor.id}")
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_retrieve_fazenda(self):
        fazenda = Fazendas.objects.create(
            nome="Fazenda Teste", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("500")
        )
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/fazendas/{fazenda.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Fazenda Teste")
        self.assertIn("area_agricultavel", response.data)
        self.assertIn("area_vegetacao", response.data)
    
    def test_update_fazenda(self):
        fazenda = Fazendas.objects.create(
            nome="Fazenda Original", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("500")
        )
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        data = {
            "nome": "Fazenda Atualizada",
            "produtor": self.produtor.id,
            "cidade": self.cidade2.id,
            "area_total": "600.00"
        }
        
        response = self.client.patch(f"/api/brainagriculture/v1/fazendas/{fazenda.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        fazenda.refresh_from_db()
        self.assertEqual(fazenda.nome, "Fazenda Atualizada")
        self.assertEqual(fazenda.cidade.id, self.cidade2.id)
        self.assertEqual(fazenda.area_total, Decimal("600.00"))
    
    def test_delete_fazenda(self):
        fazenda = Fazendas.objects.create(
            nome="Fazenda Delete", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("100")
        )
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.delete(f"/api/brainagriculture/v1/fazendas/{fazenda.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Fazendas.objects.count(), 0)
    
    def test_area_info_endpoint(self):
        fazenda = Fazendas.objects.create(
            nome="Fazenda Info", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("1000")
        )
        safra = Safras.objects.create(fazenda=fazenda, ano=2025)
        Culturas.objects.create(nome="Soja", safra=safra, area_plantada=Decimal("300"))
        Culturas.objects.create(nome="Milho", safra=safra, area_plantada=Decimal("200"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/fazendas/{fazenda.id}/area_info/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fazenda"], "Fazenda Info")
        self.assertEqual(response.data["ano"], 2025)
        self.assertIn("area_total", response.data)
        self.assertIn("area_agricultavel", response.data)
        self.assertIn("area_vegetacao", response.data)
        self.assertIn("safras", response.data)
        self.assertEqual(len(response.data["safras"]), 1)
        self.assertEqual(len(response.data["safras"][0]["culturas"]), 2)
        
        response = self.client.get(f"/api/brainagriculture/v1/fazendas/{fazenda.id}/area_info/?ano=2023")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ano"], 2023)
        self.assertEqual(len(response.data["safras"]), 0)
        
        response = self.client.get(f"/api/brainagriculture/v1/fazendas/{fazenda.id}/area_info/?ano=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SafraAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nome="Usuário", cpf_cnpj="58859042003", password="userpass123"
        )
        
        self.user2 = User.objects.create_user(
            nome="Usuário 2", cpf_cnpj="48665829016", password="userpass123"
        )

        self.produtor = Produtores.objects.create(usuario=self.user)
        self.user.produtor_perfil = self.produtor
        self.user.save()
        
        self.produtor2 = Produtores.objects.create(usuario=self.user2)
        self.user2.produtor_perfil = self.produtor2
        self.user2.save()

        self.estado = Estados.objects.create(nome="MG", sigla="MG", codigo_ibge=10)
        self.cidade = Cidades.objects.create(nome="BH", estado=self.estado, codigo_ibge=11)

        self.fazenda = Fazendas.objects.create(
            nome="Fazenda Safra", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("1000")
        )
        
        self.fazenda2 = Fazendas.objects.create(
            nome="Fazenda Outro", produtor=self.produtor2, cidade=self.cidade, area_total=Decimal("500")
        )

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_criar_safra_sucesso(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "fazenda": self.fazenda.id,
            "ano": 2024,
            "area_vegetacao_total": "300.00"
        }

        response = self.client.post("/api/brainagriculture/v1/safras/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Safras.objects.count(), 1)
        self.assertEqual(response.data["nome"], "Safra de 2024")
    
    def test_criar_safra_fazenda_outro_usuario(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "fazenda": self.fazenda2.id,
            "ano": 2024,
            "area_vegetacao_total": "100.00"
        }

        response = self.client.post("/api/brainagriculture/v1/safras/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_criar_safra_duplicada(self):
        Safras.objects.create(fazenda=self.fazenda, ano=2024)
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "fazenda": self.fazenda.id,
            "ano": 2024,
            "area_vegetacao_total": "300.00"
        }

        response = self.client.post("/api/brainagriculture/v1/safras/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_listar_safras(self):
        Safras.objects.create(fazenda=self.fazenda, ano=2023)
        Safras.objects.create(fazenda=self.fazenda, ano=2024)
        Safras.objects.create(fazenda=self.fazenda2, ano=2024)
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get("/api/brainagriculture/v1/safras/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_filtrar_safras(self):
        safra1 = Safras.objects.create(fazenda=self.fazenda, ano=2023)
        safra2 = Safras.objects.create(fazenda=self.fazenda, ano=2024)
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/safras/?ano=2023")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["ano"], 2023)
        
        response = self.client.get(f"/api/brainagriculture/v1/safras/?fazenda={self.fazenda.id}")
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_retrieve_safra(self):
        safra = Safras.objects.create(fazenda=self.fazenda, ano=2024)
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/safras/{safra.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ano"], 2024)
        self.assertIn("area_agricultavel_disponivel", response.data)
    
    def test_delete_safra(self):
        safra = Safras.objects.create(fazenda=self.fazenda, ano=2024)
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.delete(f"/api/brainagriculture/v1/safras/{safra.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Safras.objects.count(), 0)
    
    def test_culturas_resumo_endpoint(self):
        safra = Safras.objects.create(fazenda=self.fazenda, ano=2024)
        Culturas.objects.create(nome="Soja", safra=safra, area_plantada=Decimal("400"))
        Culturas.objects.create(nome="Milho", safra=safra, area_plantada=Decimal("300"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/safras/{safra.id}/culturas_resumo/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["safra"], safra.nome)
        self.assertEqual(response.data["fazenda"], self.fazenda.nome)
        self.assertEqual(response.data["ano"], 2024)
        self.assertIn("area_total_fazenda", response.data)
        self.assertIn("area_agricultavel", response.data)
        self.assertIn("area_vegetacao_total", response.data)
        self.assertIn("area_disponivel", response.data)
        self.assertIn("total_culturas", response.data)
        self.assertIn("percentual_utilizacao", response.data)
        self.assertIn("culturas_detalhes", response.data)
        self.assertEqual(response.data["total_culturas"], 2)


class CulturaValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nome="Teste", cpf_cnpj="23677269067", password="testpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user
        )

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP", codigo_ibge=5)
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado, codigo_ibge=6)

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
            nome="Teste", cpf_cnpj="99790845022", password="testpass123"
        )

        self.produtor = Produtores.objects.create(
            usuario=self.user
        )

        self.estado = Estados.objects.create(nome="São Paulo", sigla="SP", codigo_ibge=7)
        self.cidade = Cidades.objects.create(nome="Campinas", estado=self.estado, codigo_ibge=8)

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


class CulturaAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nome="Usuário", cpf_cnpj="98606476072", password="userpass123"
        )
        
        self.user2 = User.objects.create_user(
            nome="Usuário 2", cpf_cnpj="65695647061", password="userpass123"
        )
        
        self.admin_user = User.objects.create_user(
            nome="Admin", cpf_cnpj="98106090000", password="adminpass123", is_admin=True
        )

        self.produtor = Produtores.objects.create(usuario=self.user)
        self.user.produtor_perfil = self.produtor
        self.user.save()
        
        self.produtor2 = Produtores.objects.create(usuario=self.user2)
        self.user2.produtor_perfil = self.produtor2
        self.user2.save()

        self.estado = Estados.objects.create(nome="RJ", sigla="RJ", codigo_ibge=20)
        self.cidade = Cidades.objects.create(nome="Rio", estado=self.estado, codigo_ibge=21)

        self.fazenda = Fazendas.objects.create(
            nome="Fazenda Cultura", produtor=self.produtor, cidade=self.cidade, area_total=Decimal("2000")
        )
        
        self.fazenda2 = Fazendas.objects.create(
            nome="Fazenda Outro", produtor=self.produtor2, cidade=self.cidade, area_total=Decimal("1000")
        )

        self.safra = Safras.objects.create(fazenda=self.fazenda, ano=2024)
        self.safra2 = Safras.objects.create(fazenda=self.fazenda, ano=2023)
        self.safra_outro = Safras.objects.create(fazenda=self.fazenda2, ano=2024)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_criar_cultura_sucesso(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Soja",
            "safra": self.safra.id,
            "area_plantada": "500.00"
        }

        response = self.client.post("/api/brainagriculture/v1/culturas/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Culturas.objects.count(), 1)
        self.assertEqual(response.data["nome"], "Soja")
    
    def test_criar_cultura_safra_outro_usuario(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Milho",
            "safra": self.safra_outro.id,
            "area_plantada": "300.00"
        }

        response = self.client.post("/api/brainagriculture/v1/culturas/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_criar_cultura_area_invalida(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Trigo",
            "safra": self.safra.id,
            "area_plantada": "0"
        }

        response = self.client.post("/api/brainagriculture/v1/culturas/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_criar_cultura_area_excede_limite(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "nome": "Algodão",
            "safra": self.safra.id,
            "area_plantada": "3000.00"
        }

        response = self.client.post("/api/brainagriculture/v1/culturas/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_listar_culturas(self):
        Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("400"))
        Culturas.objects.create(nome="Milho", safra=self.safra, area_plantada=Decimal("300"))
        Culturas.objects.create(nome="Trigo", safra=self.safra2, area_plantada=Decimal("200"))
        Culturas.objects.create(nome="Algodão", safra=self.safra_outro, area_plantada=Decimal("100"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get("/api/brainagriculture/v1/culturas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
    
    def test_listar_culturas_admin(self):
        Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("400"))
        Culturas.objects.create(nome="Milho", safra=self.safra_outro, area_plantada=Decimal("300"))
        
        token = self.get_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get("/api/brainagriculture/v1/culturas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_filtrar_culturas(self):
        cultura1 = Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("400"))
        cultura2 = Culturas.objects.create(nome="Milho", safra=self.safra, area_plantada=Decimal("300"))
        cultura3 = Culturas.objects.create(nome="Soja", safra=self.safra2, area_plantada=Decimal("200"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/culturas/?nome=Soja")
        self.assertEqual(len(response.data["results"]), 2)
        
        response = self.client.get(f"/api/brainagriculture/v1/culturas/?safra={self.safra.id}")
        self.assertEqual(len(response.data["results"]), 2)
        
        response = self.client.get(f"/api/brainagriculture/v1/culturas/?safra__fazenda={self.fazenda.id}")
        self.assertEqual(len(response.data["results"]), 3)
        
        response = self.client.get(f"/api/brainagriculture/v1/culturas/?safra__ano=2023")
        self.assertEqual(len(response.data["results"]), 1)
    
    def test_retrieve_cultura(self):
        cultura = Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("500"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/culturas/{cultura.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Soja")
        self.assertEqual(response.data["area_plantada"], "500.00")
        self.assertIn("safra_nome", response.data)
        self.assertIn("fazenda_nome", response.data)
        self.assertIn("ano_safra", response.data)
    
    def test_update_cultura(self):
        cultura = Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("400"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        data = {
            "nome": "Soja Transgênica",
            "area_plantada": "450.00"
        }
        
        response = self.client.patch(f"/api/brainagriculture/v1/culturas/{cultura.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cultura.refresh_from_db()
        self.assertEqual(cultura.nome, "Soja Transgênica")
        self.assertEqual(cultura.area_plantada, Decimal("450.00"))
    
    def test_update_cultura_area_excede_limite(self):
        cultura1 = Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("900.00"))
        cultura2 = Culturas.objects.create(nome="Milho", safra=self.safra, area_plantada=Decimal("900.00"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        data = {
            "area_plantada": "1500.00"
        }
        
        response = self.client.patch(f"/api/brainagriculture/v1/culturas/{cultura1.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_cultura(self):
        cultura = Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("300"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.delete(f"/api/brainagriculture/v1/culturas/{cultura.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Culturas.objects.count(), 0)
    
    def test_area_disponivel_endpoint(self):
        cultura = Culturas.objects.create(nome="Soja", safra=self.safra, area_plantada=Decimal("600"))
        Culturas.objects.create(nome="Milho", safra=self.safra, area_plantada=Decimal("400"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/culturas/{cultura.id}/area_disponivel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cultura"], "Soja")
        self.assertEqual(response.data["safra"], self.safra.nome)
        self.assertEqual(response.data["fazenda"], self.fazenda.nome)
        self.assertIn("area_atual", response.data)
        self.assertIn("area_agricultavel_total", response.data)
        self.assertIn("area_outras_culturas", response.data)
        self.assertIn("area_disponivel_para_expansao", response.data)
        self.assertIn("area_maxima_possivel", response.data)
        self.assertIn("percentual_utilizacao", response.data)
        self.assertEqual(response.data["area_atual"], Decimal("600.00"))
        self.assertEqual(response.data["area_outras_culturas"], Decimal("400.00"))
    
    def test_permissoes_cultura_outro_usuario(self):
        cultura = Culturas.objects.create(nome="Soja", safra=self.safra_outro, area_plantada=Decimal("300"))
        
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = self.client.get(f"/api/brainagriculture/v1/culturas/{cultura.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.patch(f"/api/brainagriculture/v1/culturas/{cultura.id}/", {"nome": "Milho"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.delete(f"/api/brainagriculture/v1/culturas/{cultura.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
