from django.urls import path

from .views import *

urlpatterns = [
    path(
        "localidades/",
        AtualizarLocalidadesIBGEView.as_view(),
        name="atualizar-localidades",
    ),
]
