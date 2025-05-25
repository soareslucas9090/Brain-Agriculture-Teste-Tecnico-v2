from django.urls import include

app_name = "usuarios"

urlpatterns = [
    path("api/usuarios/v1/", include("Usuarios.usuarios.urls"), name="usuarios"),
]
