# Generated by Django 4.2.6 on 2023-12-08 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_cloud_app', '0004_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='link_for_download',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='date_download',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='description',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='file_path',
            field=models.FilePathField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='path',
            field=models.FilePathField(blank=True, null=True),
        ),
    ]