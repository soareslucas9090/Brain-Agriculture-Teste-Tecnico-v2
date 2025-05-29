from django.urls import include, path

app_name = "brain-agriculture"

urlpatterns = [
    path("", include("BrainAgriculture.fazendas.urls")),
    path("", include("BrainAgriculture.dashboards.urls")),
]
