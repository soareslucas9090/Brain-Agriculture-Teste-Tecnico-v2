import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BrainAgricultureTesteV2.settings")
django.setup()

from django.contrib.auth.hashers import make_password

from BrainAgriculture.fazendas.models import Culturas, Fazendas, Safras
from Common.localidades.models import Cidades
from Usuarios.produtores.models import Produtores
from Usuarios.usuarios.models import Usuarios

user1 = Usuarios.objects.create(
    cpf_cnpj="71842388002",
    nome="Usuário Um Da Silva",
    password=make_password("12345678"),
)
user2 = Usuarios.objects.create(
    cpf_cnpj="97533461070",
    nome="Usuário Dois Soares de Almeida",
    password=make_password("12345678"),
)
user3 = Usuarios.objects.create(
    cpf_cnpj="38213704000115",
    nome="Usuário Três Santos",
    password=make_password("12345678"),
)

produtor1 = Produtores.objects.create(usuario=user1)
produtor2 = Produtores.objects.create(usuario=user2)
produtor3 = Produtores.objects.create(usuario=user3)

cidade1 = Cidades.objects.get(id=302)
cidade2 = Cidades.objects.get(id=4632)
cidade3 = Cidades.objects.get(id=2113)

fazenda1 = Fazendas.objects.create(
    nome="Fazenda Um", produtor=produtor1, cidade=cidade1, area_total=150
)
fazenda2 = Fazendas.objects.create(
    nome="Fazenda Dois", produtor=produtor2, cidade=cidade2, area_total=250
)
fazenda3 = Fazendas.objects.create(
    nome="Fazenda Três", produtor=produtor3, cidade=cidade3, area_total=300
)

safra1_1 = Safras.objects.create(fazenda=fazenda1, ano=2024)
safra1_2 = Safras.objects.create(fazenda=fazenda1, ano=2025)

safra2_1 = Safras.objects.create(fazenda=fazenda2, ano=2024)
safra2_2 = Safras.objects.create(fazenda=fazenda2, ano=2025)

safra3_1 = Safras.objects.create(fazenda=fazenda3, ano=2024)
safra3_2 = Safras.objects.create(fazenda=fazenda3, ano=2025)

cultura1_1_1 = Culturas.objects.create(nome="Café", safra=safra1_1, area_plantada=50)
cultura1_1_2 = Culturas.objects.create(nome="Arroz", safra=safra1_1, area_plantada=50)
cultura1_2_1 = Culturas.objects.create(nome="Café", safra=safra1_2, area_plantada=50)
cultura1_2_2 = Culturas.objects.create(nome="Arroz", safra=safra1_2, area_plantada=100)

cultura2_1_1 = Culturas.objects.create(nome="Manga", safra=safra2_1, area_plantada=100)
cultura2_1_2 = Culturas.objects.create(nome="Feijão", safra=safra2_1, area_plantada=150)
cultura2_2_1 = Culturas.objects.create(nome="Manga", safra=safra2_2, area_plantada=120)
cultura2_2_2 = Culturas.objects.create(nome="Feijão", safra=safra2_2, area_plantada=120)

cultura3_1_1 = Culturas.objects.create(
    nome="Pimenta", safra=safra3_1, area_plantada=100
)
cultura3_1_2 = Culturas.objects.create(nome="Caju", safra=safra3_1, area_plantada=150)
cultura3_2_1 = Culturas.objects.create(
    nome="Pimenta", safra=safra3_2, area_plantada=120
)
cultura3_2_2 = Culturas.objects.create(nome="Caju", safra=safra3_2, area_plantada=140)
