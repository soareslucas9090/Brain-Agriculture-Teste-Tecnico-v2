from django.urls import include, path

app_name = "common"

urlpatterns = [
    path("localidades/", include("Common.localidades.urls"), name="localidades"),
]
