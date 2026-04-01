from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_alter_speaker_options_speaker_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='platform',
            field=models.CharField(default='telegram', max_length=10, verbose_name='Платформа'),
        ),
    ]
