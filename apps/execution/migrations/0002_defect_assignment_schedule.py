from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('execution', '0001_initial')]
    operations = [
        migrations.AddField(model_name='defectreport', name='assigned_engineer', field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AddField(model_name='defectreport', name='expected_start_date', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='defectreport', name='expected_completion_date', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='defectreport', name='manager_notes', field=models.TextField(blank=True, default='')),
    ]
