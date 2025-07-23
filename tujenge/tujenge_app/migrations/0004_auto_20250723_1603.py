from django.db import migrations

def create_chama1(apps, schema_editor):
    Chama = apps.get_model('tujenge_app', 'Chama')
    if not Chama.objects.filter(name="chama1").exists():
        Chama.objects.create(name="chama1", description="Default chama")

class Migration(migrations.Migration):

    dependencies = [
        ('tujenge_app', '0001_initial'),  # Make sure this matches your last migration
    ]

    operations = [
        migrations.RunPython(create_chama1),
    ]