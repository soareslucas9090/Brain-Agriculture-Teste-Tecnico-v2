from django.urls import include, path

app_name = "usuarios"

urlpatterns = [
    path("", include("Usuarios.usuarios.urls"), name="usuarios"),
    path(
        "",
        include("Usuarios.produtores.urls"),
        name="produtores",
    ),
]
