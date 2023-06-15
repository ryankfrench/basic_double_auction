# Generated by Django 4.2 on 2023-05-16 22:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_parameterset_reconnection_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterSetPlayerType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_id', models.IntegerField(default=0, verbose_name='Type ID')),
                ('budget', models.IntegerField(default=0, verbose_name='Budget')),
                ('units', models.IntegerField(default=0, verbose_name='Units')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameter_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_player_types', to='main.parameterset')),
            ],
            options={
                'verbose_name': 'Parameter Set Player Type',
                'verbose_name_plural': 'Parameter Set Player Types',
                'ordering': ['type_id'],
            },
        ),
        migrations.AddField(
            model_name='parametersetplayer',
            name='parameter_set_player_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_players_b', to='main.parametersetplayertype'),
        ),
    ]
