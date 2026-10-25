import common.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
    ]
    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Създадено на')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновено на')),
                ('case_number', models.CharField(editable=False, max_length=12, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_case_number', message='Номерът на досието трябва да е във формат CC-ГГГГ-NNNN.', regex='^CC-\\d{4}-\\d{4}$')], verbose_name='Номер на досието')),
                ('title', models.CharField(max_length=120, verbose_name='Заглавие')),
                ('description', models.TextField(verbose_name='Описание')),
                ('crime_date', models.DateField(validators=[common.validators.NotInFutureValidator()], verbose_name='Дата на престъплението')),
                ('location', models.CharField(max_length=150, verbose_name='Място')),
                ('victim', models.CharField(blank=True, max_length=120, verbose_name='Жертва')),
                ('status', models.CharField(choices=[('open', 'Открит'), ('solved', 'Разкрит'), ('frozen', 'Замразен')], default='open', max_length=10, verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Досие',
                'verbose_name_plural': 'Досиета',
                'ordering': ['-crime_date', '-created_at'],
            },
        ),
    ]
