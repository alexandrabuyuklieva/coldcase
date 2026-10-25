import common.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suspect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Създадено на')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновено на')),
                ('first_name', models.CharField(max_length=50, verbose_name='Име')),
                ('last_name', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('alias', models.CharField(blank=True, max_length=50, verbose_name='Прякор')),
                ('date_of_birth', models.DateField(blank=True, null=True, validators=[common.validators.NotInFutureValidator()], verbose_name='Дата на раждане')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('photo_url', models.URLField(blank=True, verbose_name='Снимка (URL)')),
                ('cases', models.ManyToManyField(blank=True, related_name='suspects', to='cases.case', verbose_name='Досиета')),
            ],
            options={
                'verbose_name': 'Заподозрян',
                'verbose_name_plural': 'Заподозрени',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Alibi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Създадено на')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновено на')),
                ('location', models.CharField(max_length=150, verbose_name='Място')),
                ('starts_at', models.DateTimeField(verbose_name='От')),
                ('ends_at', models.DateTimeField(verbose_name='До')),
                ('witness', models.CharField(blank=True, max_length=120, verbose_name='Свидетел')),
                ('notes', models.TextField(blank=True, verbose_name='Бележки')),
                ('suspect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alibis', to='suspects.suspect', verbose_name='Заподозрян')),
            ],
            options={
                'verbose_name': 'Алиби',
                'verbose_name_plural': 'Алибита',
                'ordering': ['starts_at'],
            },
        ),
    ]
