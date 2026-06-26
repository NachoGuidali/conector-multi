from django.db import migrations, models


def backfill_numeros(apps, schema_editor):
    NumeroWhatsApp = apps.get_model('whatsapp', 'NumeroWhatsApp')
    User = apps.get_model('users', 'User')
    numero = NumeroWhatsApp.objects.order_by('pk').first()
    if not numero:
        return
    for user in User.objects.filter(rol='agente'):
        user.numeros.add(numero)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_user_recibe_asignaciones'),
        ('whatsapp', '0006_backfill_numero'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='numeros',
            field=models.ManyToManyField(
                blank=True,
                related_name='agentes',
                to='whatsapp.numerowhatsapp',
                verbose_name='Números de WhatsApp asignados',
            ),
        ),
        migrations.RunPython(backfill_numeros, noop),
    ]
