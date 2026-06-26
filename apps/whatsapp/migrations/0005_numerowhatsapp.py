import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('whatsapp', '0004_conversacion_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumeroWhatsApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Etiqueta visible: "Ventas", "Soporte"...', max_length=100)),
                ('instance_name', models.SlugField(help_text='Nombre de instancia en Evolution API', max_length=100, unique=True)),
                ('telefono', models.CharField(blank=True, max_length=20)),
                ('evolution_api_url', models.CharField(blank=True, help_text='Vacío = usar el default global', max_length=300)),
                ('evolution_api_key', models.CharField(blank=True, help_text='Vacío = usar el default global', max_length=300)),
                ('webhook_token', models.CharField(blank=True, max_length=200)),
                ('estado_conexion', models.CharField(choices=[('open', 'Conectado'), ('close', 'Desconectado'), ('connecting', 'Conectando')], default='close', max_length=20)),
                ('activo', models.BooleanField(default=True)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Número de WhatsApp',
                'verbose_name_plural': 'Números de WhatsApp',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.AddField(
            model_name='conversacion',
            name='numero',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='conversaciones',
                to='whatsapp.numerowhatsapp',
            ),
        ),
    ]
