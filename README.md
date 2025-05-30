

#  Brain Agriculture - Teste Técnico v2

<img  align="center"  alt="Python"  width="30"  src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"><span>&nbsp;&nbsp;&nbsp;</span><img  align="center"  alt="Django"  width="30"  src="https://cdn.worldvectorlogo.com/logos/django.svg"><span>&nbsp;&nbsp;&nbsp;</span><img  align="center"  alt="Django Rest Framework"  height="40"  src="https://i.imgur.com/dcVFAeV.png"><span>&nbsp;&nbsp;&nbsp;</span><img  align="center"  alt="PostgreSQL"  width="36"  src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postgresql/postgresql-original.svg"><span>&nbsp;&nbsp;&nbsp;</span>
  

## Sobre o Projeto

O projeto foi feitro com Django e Django Rest Framework, usando algumas libs, como Django Filter, para facilitar as pesquisas por query params, Django Simple History, para tornar rastreável as alterações no banco e nos dados, sentry para rastrear erros inesperados/não tratados, entre outras incluídas no projeto.

  

## Recursos implementados

1.  Cadastro, edição e exclusão de produtores rurais.
2.  CPF e CNPJ validados.
3.  Garantia que a soma das áreas agricultável e de vegetação não ultrapasse a área total da fazenda.
4.  Permite o registro de várias culturas plantadas por fazenda do produtor.
5.  Um produtor pode estar associado a 0, 1 ou mais propriedades rurais.
6.  Uma propriedade rural pode ter 0, 1 ou mais culturas plantadas por safra.
7.  Endpoint de dashboards com:
    -   Total de fazendas cadastradas (quantidade).
    -   Total de hectares registrados (área total).
    -   Por estado.
    -   Por cultura plantada.
    -   Por uso do solo (área agricultável e vegetação).

- Gerenciamento de permissões de acordo com o tipo de usuário.

- Segurança e gerenciamento para os dados pertencentes ao usuário requisitante, ou não.

- Personalização de views de acordo com permissões de usuário

- Segurança baseada em tokens jwt (access e refresh tokens)

- Documentação Swagger Completa

### Sem tempo para implementar

Algumas funcionalidades foram planejadas, mas não houve tempo de implementar de maneira eficiente, sendo:

- Dashboards montados e exportados em PDF. Iria ser usado a S3 da amazon para armazenar e retornar o link dos arquivos via endpoint de dashboards.

- Suporte a Cache em Banco (Redis)


## Segurança

  

A API foi implementada com autenticação SimpleJWT, usando Django Rest Framework, a documentação foi feita com Swagger, via DRF-Spectacular, sendo totalmente funcional e testável.

A documentação Swagger está na rota `/api/schema/swagger/`

  

## Rodando o projeto

  

Primeiro é necessária a criação de um Ambiente Virtual do Python (necessário versão 3.8 ou posterior do Python, mas recomendamos a 3.12), ou `venv`, para isso basta executar `python -m venv venv`. Ao término é necessário ativar a venv, então na mesma pasta que foi criado a pasta do ambiente virtual, rode o comando `venv\scripts\activate` para Windows, ou `venv/bin/activate` praa Linux, e pronto.

  

Para instalar as dependências é necesário rodar o comando `pip install -r requirements.txt` com o Ambiente Virtual Ativo.

O código busca um arquivo `.env` para procurar as variáveis de ambiente necessárias, e caso não ache, usará as variáveis de ambiente instaladas no SO. O arquivo deve seguir os seguintes moldes:

```
DB_PASSWORD=Senha do banco
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_HOST=Host do banco
DB_PORT=Porta do banco
DJANGO_SECRET_KEY=Chave secreta do Django
IBGE_ESTADOS_API_URL=https://servicodados.ibge.gov.br/api/v1/localidades/estados
IBGE_MUCICIPIOS_API_URL=https://servicodados.ibge.gov.br/api/v1/localidades/municipios
DSN_SENTRY=DSN do Sentry
```

Colocar o arquivo `.env` na raiz do projeto ou adicionar estas variáveis diretamente no sistema.

  

Faça a criação do banco de dados com o comando `python manage.py migrate`.


Execute um `python manage.py collectstatic` para criar os arquivos estáticos da documentação da API, pois sem este comando, o Swagger não consegue executar os arquivos CSS e JS necessários para rodar a sua interface.

Crie um super usuário com o comando `python manage.py createsuperuser` e forneça os dados que vão ser pedidos.

O servidor para rodar o sistema em um computador Linux é o "Gunicorn", e o comando é:

`gunicorn BrainAgricultureTesteV2.wsgi --workers 2 --bind :8000 --access-logfile -`

## Testes

Foram implementados testes em todos os apps, menos no app de "localidades", que não era um requisito da tarefa, e há pouca coisa a ser testada (apenas a integração com a API do IBGE, que já foi consumida e o banco alimentado com todos os estados e municípios).
Para executar os testes é necessário apenas rodar o comando `python manage.py test` ou, caso queira rodar app por app, os comandos podem ser os seguintes:
- `python manage.py test Usuarios.usuarios.tests` para o app de "usuarios".
- `python manage.py test Usuarios.produtores.tests` para o app de "produtores".
- `python manage.py test BrainAgriculture.fazendas.tests` para o app de "fazendas".
- `python manage.py test BrainAgriculture.dashboards.tests` para o app de "dashboards".

## Dados Mockados
Foram mockados alguns dados, a fim de facilitar os testes pela equipe técnica. Os usuários para testar o sistema estão listados abaixo:
|Nome|CPF / CNPJ (login)|Senha|Tipo|
|-|-|-|-|
|Admin|11111111111|12345678|Admin|
|Usuário Um Da Silva|71842388002|12345678|Usuário comum|
|Usuário Dois Soares de Almeida|97533461070|12345678|Usuário comum|
|Usuário Três Santos|38213704000115|12345678|Usuário comum|

Os dados da outras tabelas também já estão mockados e prontos para serem consumidos.


## Autenticação

  

O Access Token da API tem duração de 15 minutos, enquanto o Refresh Token tem duração de 60 minutos. Estes valores podem ser mudados no arquivo `BrainAgricultureTesteV2\rest_frameword_settings.py` em `ACCESS_TOKEN_LIFETIME` e `REFRESH_TOKEN_LIFETIME`.

  

A autenticação da API segue o padrão Bearer Token, onde o Header `Authorization` deve conter o valor `Bearer SeuTokenDeAcessoAqui`.
