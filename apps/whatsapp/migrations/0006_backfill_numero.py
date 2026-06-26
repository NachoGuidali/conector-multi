from django.conf import settings
from django.db import migrations, models


def backfill_numero(apps, schema_editor):
    NumeroWhatsApp = apps.get_model('whatsapp', 'NumeroWhatsApp')
    ConfiguracionWhatsApp = apps.get_model('whatsapp', 'ConfiguracionWhatsApp')
    Conversacion = apps.get_model('whatsapp', 'Conversacion')

    old_config = ConfiguracionWhatsApp.objects.filter(pk=1).first()
    numero = NumeroWhatsApp.objects.create(
        nombre='Principal',
        instance_name=(old_config.evolution_instance_name if old_config else None)
            or getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'waply'),
        evolution_api_url=old_config.evolution_api_url if old_config else '',
        evolution_api_key=old_config.evolution_api_key if old_config else '',
        webhook_token=old_config.webhook_token if old_config else '',
    )
    Conversacion.objects.filter(numero__isnull=True).update(numero=numero)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('whatsapp', '0005_numerowhatsapp'),
    ]

    operations = [
        migrations.RunPython(backfill_numero, noop),
        migrations.AlterField(
            model_name='conversacion',
            name='numero',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='conversaciones',
                to='whatsapp.numerowhatsapp',
            ),
        ),
        migrations.AlterField(
            model_name='conversacion',
            name='telefono',
            field=models.CharField(db_index=True, max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='conversacion',
            unique_together={('numero', 'telefono')},
        ),
        migrations.DeleteModel(
            name='ConfiguracionWhatsApp',
        ),
    ]
