from rest_framework.permissions import IsAuthenticated

from Core.Permissions import EhMeuDadoOuSouAdmin

from .BasicModelViewSet import BasicModelViewSet


class BasicMyDataAndModelViewSet(BasicModelViewSet):
    def get_permissions(self):
        if self.action == "retrieve":
            return [EhMeuDadoOuSouAdmin()]
        return [IsAuthenticated()]
