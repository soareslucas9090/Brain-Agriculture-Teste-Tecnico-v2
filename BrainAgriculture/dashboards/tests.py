from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from Common.localidades.models import Estados, Cidades
from Usuarios.produtores.models import Produtores
from BrainAgriculture.fazendas.models import Fazendas, Safras, Culturas
from .business import DashboardBusiness

User = get_user_model()


class DashboardBusinessTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            cpf_cnpj='66484750050',
            password='senha123',
            nome='Usuário Teste'
        )
        
        self.sp = Estados.objects.create(nome='São Paulo', sigla='SP', codigo_ibge=1)
        self.mg = Estados.objects.create(nome='Minas Gerais', sigla='MG', codigo_ibge=2)
        
        self.cidade_sp = Cidades.objects.create(
            nome='São Paulo',
            estado=self.sp,
            codigo_ibge=3
        )
        self.cidade_mg = Cidades.objects.create(
            nome='Belo Horizonte',
            estado=self.mg,
            codigo_ibge=4
        )
        
        self.produtor = Produtores.objects.create(
            usuario=self.user,
        )
        
        self.fazenda_sp1 = Fazendas.objects.create(
            nome='Fazenda SP 1',
            produtor=self.produtor,
            cidade=self.cidade_sp,
            area_total=Decimal('100.00')
        )
        self.fazenda_sp2 = Fazendas.objects.create(
            nome='Fazenda SP 2',
            produtor=self.produtor,
            cidade=self.cidade_sp,
            area_total=Decimal('150.00')
        )
        self.fazenda_mg = Fazendas.objects.create(
            nome='Fazenda MG',
            produtor=self.produtor,
            cidade=self.cidade_mg,
            area_total=Decimal('200.00')
        )
        
        self.ano_atual = datetime.now().year
        
        self.safra_sp1 = Safras.objects.create(
            fazenda=self.fazenda_sp1,
            ano=self.ano_atual
        )
        Culturas.objects.create(
            nome='Soja',
            safra=self.safra_sp1,
            area_plantada=Decimal('50.00')
        )
        Culturas.objects.create(
            nome='Milho',
            safra=self.safra_sp1,
            area_plantada=Decimal('30.00')
        )
        
        self.safra_mg = Safras.objects.create(
            fazenda=self.fazenda_mg,
            ano=self.ano_atual
        )
        Culturas.objects.create(
            nome='Soja',
            safra=self.safra_mg,
            area_plantada=Decimal('100.00')
        )
        Culturas.objects.create(
            nome='Café',
            safra=self.safra_mg,
            area_plantada=Decimal('50.00')
        )
    
    def test_get_totais(self):
        totais = DashboardBusiness.get_totais()
        
        self.assertEqual(totais['total_fazendas'], 3)
        self.assertEqual(totais['total_hectares'], Decimal('450.00'))
    
    def test_get_distribuicao_por_estado(self):
        distribuicao = DashboardBusiness.get_distribuicao_por_estado()
        
        self.assertEqual(len(distribuicao), 2)
        
        sp_data = next(d for d in distribuicao if d['sigla'] == 'SP')
        self.assertEqual(sp_data['quantidade'], 2)
        self.assertEqual(sp_data['percentual'], 66.67)
        
        mg_data = next(d for d in distribuicao if d['sigla'] == 'MG')
        self.assertEqual(mg_data['quantidade'], 1)
        self.assertEqual(mg_data['percentual'], 33.33)
    
    def test_get_distribuicao_por_cultura(self):
        distribuicao = DashboardBusiness.get_distribuicao_por_cultura()
        
        self.assertEqual(len(distribuicao), 3)
        
        soja_data = next(d for d in distribuicao if d['cultura'] == 'Soja')
        self.assertEqual(soja_data['area_total'], Decimal('150.00'))
        
        cafe_data = next(d for d in distribuicao if d['cultura'] == 'Café')
        self.assertEqual(cafe_data['area_total'], Decimal('50.00'))
        
        milho_data = next(d for d in distribuicao if d['cultura'] == 'Milho')
        self.assertEqual(milho_data['area_total'], Decimal('30.00'))
    
    def test_get_uso_solo(self):
        uso_solo = DashboardBusiness.get_uso_solo(self.ano_atual)
        
        self.assertEqual(len(uso_solo), 2)
        
        # Área total: 450 hectares
        # Área com vegetação (culturas): 230 hectares
        # Área agricultável: 220 hectares
        
        agricultavel = next(d for d in uso_solo if d['tipo'] == 'Área Agricultável')
        self.assertEqual(agricultavel['area_total'], Decimal('220.00'))
        
        vegetacao = next(d for d in uso_solo if d['tipo'] == 'Vegetação')
        self.assertEqual(vegetacao['area_total'], Decimal('230.00'))


class DashboardAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            cpf_cnpj='48879148060',
            password='senha123',
            nome='Usuário Teste'
        )
        
        self.estado = Estados.objects.create(nome='São Paulo', sigla='SP', codigo_ibge=1)
        self.cidade = Cidades.objects.create(
            nome='São Paulo',
            estado=self.estado,
            codigo_ibge=1
        )
        
        self.produtor = Produtores.objects.create(
            usuario=self.user
        )
        
        self.fazenda = Fazendas.objects.create(
            nome='Fazenda Teste',
            produtor=self.produtor,
            cidade=self.cidade,
            area_total=Decimal('100.00')
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_completo(self):
        response = self.client.get('/api/brainagriculture/v1/dashboards/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totais', response.data)
        self.assertIn('por_estado', response.data)
        self.assertIn('por_cultura', response.data)
        self.assertIn('uso_solo', response.data)
    
    def test_dashboard_totais(self):
        response = self.client.get('/api/brainagriculture/v1/dashboards/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_fazendas', str(response.data))
        self.assertIn('total_hectares', str(response.data))
    
    def test_dashboard_por_estado(self):
        response = self.client.get('/api/brainagriculture/v1/dashboards/por_estado/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_dashboard_por_cultura(self):
        response = self.client.get('/api/brainagriculture/v1/dashboards/por_cultura/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_dashboard_uso_solo(self):
        response = self.client.get('/api/brainagriculture/v1/dashboards/uso_solo/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_dashboard_sem_autenticacao(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/brainagriculture/v1/dashboards/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)