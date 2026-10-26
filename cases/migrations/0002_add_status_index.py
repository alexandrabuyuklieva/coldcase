
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='case',
            index=models.Index(fields=['status', '-crime_date'], name='case_status_date_idx'),
        ),
    ]
