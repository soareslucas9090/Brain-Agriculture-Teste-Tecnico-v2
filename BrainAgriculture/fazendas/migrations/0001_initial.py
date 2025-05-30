# Generated by Django 5.2.1 on 2025-05-28 05:06

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('localidades', '0002_rename_cidade_cidades_rename_estado_estados_and_more'),
        ('produtores', '0003_remove_historicalprodutores_nome_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Fazendas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, help_text='Data e hora em que o registro foi criado.', verbose_name='Data de Criação')),
                ('data_modificacao', models.DateTimeField(auto_now=True, help_text='Data e hora da última modificação do registro.', verbose_name='Data de Modificação')),
                ('nome', models.CharField(help_text='Nome do registro.', max_length=255, verbose_name='Nome')),
                ('area_total', models.DecimalField(decimal_places=2, help_text='Área total da fazenda, em hectares.', max_digits=10)),
                ('cidade', models.ForeignKey(help_text='A cidade onde a fazenda está localizada.', on_delete=django.db.models.deletion.PROTECT, related_name='fazendas', to='localidades.cidades', verbose_name='Localização da fazenda.')),
                ('produtor', models.ForeignKey(help_text='O usuário/produtor quer será associado à fazenda.', on_delete=django.db.models.deletion.PROTECT, related_name='fazendas', to='produtores.produtores', verbose_name='Proprietário da fazenda.')),
            ],
            options={
                'verbose_name': 'Fazenda',
                'verbose_name_plural': 'Fazendas',
                'ordering': ['nome'],
                'unique_together': {('nome', 'produtor')},
            },
        ),
        migrations.CreateModel(
            name='HistoricalFazendas',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(blank=True, editable=False, help_text='Data e hora em que o registro foi criado.', verbose_name='Data de Criação')),
                ('data_modificacao', models.DateTimeField(blank=True, editable=False, help_text='Data e hora da última modificação do registro.', verbose_name='Data de Modificação')),
                ('nome', models.CharField(help_text='Nome do registro.', max_length=255, verbose_name='Nome')),
                ('area_total', models.DecimalField(decimal_places=2, help_text='Área total da fazenda, em hectares.', max_digits=10)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('cidade', models.ForeignKey(blank=True, db_constraint=False, help_text='A cidade onde a fazenda está localizada.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='localidades.cidades', verbose_name='Localização da fazenda.')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('produtor', models.ForeignKey(blank=True, db_constraint=False, help_text='O usuário/produtor quer será associado à fazenda.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='produtores.produtores', verbose_name='Proprietário da fazenda.')),
            ],
            options={
                'verbose_name': 'historical Fazenda',
                'verbose_name_plural': 'historical Fazendas',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSafra',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(blank=True, editable=False, help_text='Data e hora em que o registro foi criado.', verbose_name='Data de Criação')),
                ('data_modificacao', models.DateTimeField(blank=True, editable=False, help_text='Data e hora da última modificação do registro.', verbose_name='Data de Modificação')),
                ('nome', models.CharField(help_text='Nome do registro.', max_length=255, verbose_name='Nome')),
                ('ano', models.IntegerField(help_text='Ano da safra.', verbose_name='Ano')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('fazenda', models.ForeignKey(blank=True, db_constraint=False, help_text='A fazenda relacionada à safra.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='fazendas.fazendas', verbose_name='Fazenda')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Safra',
                'verbose_name_plural': 'historical Safras',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Safra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, help_text='Data e hora em que o registro foi criado.', verbose_name='Data de Criação')),
                ('data_modificacao', models.DateTimeField(auto_now=True, help_text='Data e hora da última modificação do registro.', verbose_name='Data de Modificação')),
                ('nome', models.CharField(help_text='Nome do registro.', max_length=255, verbose_name='Nome')),
                ('ano', models.IntegerField(help_text='Ano da safra.', verbose_name='Ano')),
                ('fazenda', models.ForeignKey(help_text='A fazenda relacionada à safra.', on_delete=django.db.models.deletion.CASCADE, related_name='safras', to='fazendas.fazendas', verbose_name='Fazenda')),
            ],
            options={
                'verbose_name': 'Safra',
                'verbose_name_plural': 'Safras',
                'ordering': ['-ano'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalCultura',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(blank=True, editable=False, help_text='Data e hora em que o registro foi criado.', verbose_name='Data de Criação')),
                ('data_modificacao', models.DateTimeField(blank=True, editable=False, help_text='Data e hora da última modificação do registro.', verbose_name='Data de Modificação')),
                ('nome', models.CharField(help_text='Nome do registro.', max_length=255, verbose_name='Nome')),
                ('area_plantada', models.DecimalField(decimal_places=2, help_text='Área plantada da cultura, em hectares.', max_digits=10)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('safra', models.ForeignKey(blank=True, db_constraint=False, help_text='A safra relacionada à cultura.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='fazendas.safra', verbose_name='Safra')),
            ],
            options={
                'verbose_name': 'historical Cultura',
                'verbose_name_plural': 'historical Culturas',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Cultura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, help_text='Data e hora em que o registro foi criado.', verbose_name='Data de Criação')),
                ('data_modificacao', models.DateTimeField(auto_now=True, help_text='Data e hora da última modificação do registro.', verbose_name='Data de Modificação')),
                ('nome', models.CharField(help_text='Nome do registro.', max_length=255, verbose_name='Nome')),
                ('area_plantada', models.DecimalField(decimal_places=2, help_text='Área plantada da cultura, em hectares.', max_digits=10)),
                ('safra', models.ForeignKey(help_text='A safra relacionada à cultura.', on_delete=django.db.models.deletion.PROTECT, related_name='culturas', to='fazendas.safra', verbose_name='Safra')),
            ],
            options={
                'verbose_name': 'Cultura',
                'verbose_name_plural': 'Culturas',
                'ordering': ['safra__ano', 'nome'],
            },
        ),
    ]
