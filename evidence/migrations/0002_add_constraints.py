
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0002_add_status_index'),
        ('evidence', '0001_initial'),
        ('suspects', '0002_add_constraints'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='evidence',
            constraint=models.CheckConstraint(condition=models.Q(('confidence__lte', 100)), name='evidence_confidence_max_100', violation_error_message='Достоверността не може да е над 100%.'),
        ),
    ]
