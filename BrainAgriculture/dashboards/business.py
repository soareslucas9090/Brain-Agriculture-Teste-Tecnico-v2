from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any
from django.db.models import Sum, Count, F

from BrainAgriculture.fazendas.models import Fazendas, Culturas


class DashboardBusiness:
    @staticmethod
    def get_totais() -> Dict[str, Any]:
        """
        Retorna os totais de fazendas e hectares cadastrados.
        
        Returns:
            Dict contendo total_fazendas e total_hectares
        """
        fazendas = Fazendas.objects.filter()
        
        total_fazendas = fazendas.count()
        total_hectares = fazendas.aggregate(
            total=Sum('area_total')
        )['total'] or Decimal('0')

        return {
            'total_fazendas': total_fazendas,
            'total_hectares': total_hectares
        }

    @staticmethod
    def get_distribuicao_por_estado() -> List[Dict[str, Any]]:
        """
        Calcula a distribuição de fazendas por estado.
        
        Returns:
            Lista de dicts com estado, sigla, quantidade e percentual
        """
        fazendas_por_estado = (
            Fazendas.objects
            .filter()
            .values(
                estado=F('cidade__estado__nome'),
                sigla=F('cidade__estado__sigla')
            )
            .annotate(quantidade=Count('id'))
            .order_by('-quantidade')
        )

        total_fazendas = sum(item['quantidade'] for item in fazendas_por_estado)
        
        resultado = []
        for item in fazendas_por_estado:
            percentual = (item['quantidade'] / total_fazendas * 100) if total_fazendas > 0 else 0
            resultado.append({
                'estado': item['estado'],
                'sigla': item['sigla'],
                'quantidade': item['quantidade'],
                'percentual': round(percentual, 2)
            })

        return resultado

    @staticmethod
    def get_distribuicao_por_cultura() -> List[Dict[str, Any]]:
        """
        Calcula a distribuição de área por cultura plantada.
        
        Returns:
            Lista de dicts com cultura, area_total e percentual
        """
        culturas_area = (
            Culturas.objects
            .filter()
            .values('nome')
            .annotate(area_total=Sum('area_plantada'))
            .order_by('-area_total')
        )

        # Calcular total para percentuais
        total_area = sum(item['area_total'] for item in culturas_area)
        
        # Adicionar percentuais
        resultado = []
        for item in culturas_area:
            percentual = (float(item['area_total']) / float(total_area) * 100) if total_area > 0 else 0
            resultado.append({
                'cultura': item['nome'],
                'area_total': item['area_total'],
                'percentual': round(percentual, 2)
            })

        return resultado

    @staticmethod
    def get_uso_solo(ano_referencia: int = None) -> List[Dict[str, Any]]:
        """
        Calcula a distribuição entre área agricultável e vegetação.
        
        Args:
            ano_referencia: Ano para cálculo. Se None, usa o ano atual.
            
        Returns:
            Lista de dicts com tipo, area_total e percentual
        """
        if ano_referencia is None:
            ano_referencia = datetime.now().year
            
        fazendas = Fazendas.objects.filter()
        
        area_total = Decimal('0')
        area_vegetacao = Decimal('0')
        
        for fazenda in fazendas:
            area_total += fazenda.area_total
            area_vegetacao += fazenda.area_vegetacao(ano_referencia)
        
        area_agricultavel = area_total - area_vegetacao
        
        resultado = []
        
        if area_total > 0:
            percentual_agricultavel = float(area_agricultavel) / float(area_total) * 100
            percentual_vegetacao = float(area_vegetacao) / float(area_total) * 100
            
            resultado = [
                {
                    'tipo': 'Área Agricultável',
                    'area_total': area_agricultavel,
                    'percentual': round(percentual_agricultavel, 2)
                },
                {
                    'tipo': 'Vegetação',
                    'area_total': area_vegetacao,
                    'percentual': round(percentual_vegetacao, 2)
                }
            ]
        
        return resultado

    @staticmethod
    def get_dashboard_completo(ano_referencia: int = None) -> Dict[str, Any]:
        """
        Retorna todos os dados do dashboard de uma vez.
        
        Args:
            ano_referencia: Ano para cálculo de uso do solo. Se None, usa o ano atual.
            
        Returns:
            Dict com totais, por_estado, por_cultura e uso_solo
        """
        return {
            'totais': DashboardBusiness.get_totais(),
            'por_estado': DashboardBusiness.get_distribuicao_por_estado(),
            'por_cultura': DashboardBusiness.get_distribuicao_por_cultura(),
            'uso_solo': DashboardBusiness.get_uso_solo(ano_referencia)
        }