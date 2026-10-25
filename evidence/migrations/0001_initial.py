import common.validators
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('cases', '0001_initial'),
        ('suspects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Създадено на')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновено на')),
                ('title', models.CharField(max_length=120, verbose_name='Наименование')),
                ('evidence_type', models.CharField(choices=[('physical', 'Веществено'), ('document', 'Документ'), ('testimony', 'Свидетелски показания'), ('digital', 'Дигитално'), ('forensic', 'Криминалистична експертиза')], default='physical', max_length=20, verbose_name='Вид')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('collected_on', models.DateField(validators=[common.validators.NotInFutureValidator()], verbose_name='Дата на откриване')),
                ('found_at', models.CharField(blank=True, max_length=150, verbose_name='Място на откриване')),
                ('confidence', models.PositiveSmallIntegerField(default=50, validators=[django.core.validators.MinValueValidator(0, message='Достоверността не може да е под %(limit_value)s%%.'), django.core.validators.MaxValueValidator(100, message='Достоверността не може да е над %(limit_value)s%%.')], verbose_name='Достоверност (%)')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence', to='cases.case', verbose_name='Досие')),
                ('implicates', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='implicating_evidence', to='suspects.suspect', verbose_name='Уличава')),
            ],
            options={
                'verbose_name': 'Улика',
                'verbose_name_plural': 'Улики',
                'ordering': ['-collected_on', '-created_at'],
            },
        ),
    ]
