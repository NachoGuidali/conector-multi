from django.db import migrations, models
import django.db.models.deletion


def backfill_numero(apps, schema_editor):
    NumeroWhatsApp = apps.get_model('whatsapp', 'NumeroWhatsApp')
    Difusion = apps.get_model('difusiones', 'Difusion')
    numero = NumeroWhatsApp.objects.order_by('pk').first()
    if numero:
        Difusion.objects.filter(numero__isnull=True).update(numero=numero)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('difusiones', '0001_initial'),
        ('whatsapp', '0006_backfill_numero'),
    ]

    operations = [
        migrations.AddField(
            model_name='difusion',
            name='numero',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='difusiones',
                to='whatsapp.numerowhatsapp',
            ),
        ),
        migrations.RunPython(backfill_numero, noop),
        migrations.AlterField(
            model_name='difusion',
            name='numero',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='difusiones',
                to='whatsapp.numerowhatsapp',
            ),
        ),
    ]
