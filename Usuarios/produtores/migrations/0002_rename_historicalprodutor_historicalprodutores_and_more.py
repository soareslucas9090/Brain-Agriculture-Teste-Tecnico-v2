# Generated by Django 5.2.1 on 2025-05-25 22:55

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produtores', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HistoricalProdutor',
            new_name='HistoricalProdutores',
        ),
        migrations.RenameModel(
            old_name='Produtor',
            new_name='Produtores',
        ),
    ]
