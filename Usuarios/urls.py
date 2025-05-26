from django.urls import include, path

app_name = "usuarios"

urlpatterns = [
    path("usuarios/", include("Usuarios.usuarios.urls"), name="usuarios"),
    path(
        "produtores/",
        include("Usuarios.produtores.urls"),
        name="produtores",
    ),
]
