# Generated by Django 5.2.1 on 2025-05-25 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalusuarios',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='usuarios',
            name='is_staff',
        ),
        migrations.AddField(
            model_name='historicalusuarios',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designa se o usuário pode fazer login no site de administração (admin).', verbose_name='Superusuário'),
        ),
        migrations.AddField(
            model_name='usuarios',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designa se o usuário pode fazer login no site de administração (admin).', verbose_name='Superusuário'),
        ),
    ]
