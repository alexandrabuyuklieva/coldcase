
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suspects', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='alibi',
            constraint=models.CheckConstraint(condition=models.Q(('ends_at__gt', models.F('starts_at'))), name='alibi_ends_after_start', violation_error_message='Краят на алибито трябва да е след началото му.'),
        ),
    ]
