# Generated by Django 4.1.4 on 2022-12-14 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xk_models', '0005_classdetail_brief_classdetail_exam_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classdetail',
            name='assessment',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='classdetail',
            name='brief',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='classdetail',
            name='teacher_info',
            field=models.CharField(default='', max_length=200),
        ),
    ]