from rest_framework.viewsets import ModelViewSet


class BasicModelViewSet(ModelViewSet):
    def get_dono_do_registro(self, obj):
        raise NotImplementedError("Subclasses devem implementar get_dono_do_registro")
