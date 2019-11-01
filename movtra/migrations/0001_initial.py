# Generated by Django 2.1.3 on 2019-10-31 22:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('logo_path', models.CharField(blank=True, max_length=50, null=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('origin_country', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('iso_3166_1', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genres',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='isGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Genres')),
            ],
        ),
        migrations.CreateModel(
            name='isIn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('iso_639_1', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('rating', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=3, null=True)),
                ('review', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('adult', models.BooleanField()),
                ('belongs_to_collection', models.IntegerField(blank=True, null=True)),
                ('budget', models.IntegerField(blank=True, null=True)),
                ('homepage', models.CharField(blank=True, max_length=100, null=True)),
                ('imdb_id', models.CharField(blank=True, max_length=100, null=True)),
                ('original_language', models.CharField(blank=True, max_length=100, null=True)),
                ('original_title', models.CharField(blank=True, max_length=100, null=True)),
                ('overview', models.TextField()),
                ('popularity', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True)),
                ('backdrop_path', models.CharField(blank=True, max_length=100, null=True)),
                ('poster_path', models.CharField(blank=True, max_length=100, null=True)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('revenue', models.IntegerField(blank=True, null=True)),
                ('runtime', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('tagline', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.CharField(max_length=100)),
                ('video', models.BooleanField()),
                ('vote_average', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=3, null=True)),
                ('vote_count', models.IntegerField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Produce',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Company')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='ProductionCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Country')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='SpokenLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Language')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='WorkedAsCast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cast_id', models.IntegerField(blank=True, null=True)),
                ('character', models.CharField(blank=True, max_length=100, null=True)),
                ('credit_id', models.CharField(max_length=100)),
                ('gender', models.IntegerField(blank=True, null=True)),
                ('person_id', models.IntegerField()),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('profile_path', models.CharField(blank=True, max_length=100, null=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='WorkedAsCrew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_id', models.CharField(max_length=100)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('gender', models.IntegerField(blank=True, null=True)),
                ('person_id', models.IntegerField()),
                ('job', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('profile_path', models.CharField(blank=True, max_length=100, null=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie')),
            ],
        ),
        migrations.AddField(
            model_name='logentry',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie'),
        ),
        migrations.AddField(
            model_name='isin',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movtra.List'),
        ),
        migrations.AddField(
            model_name='isin',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie'),
        ),
        migrations.AddField(
            model_name='isgenre',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='movtra.Movie'),
        ),
        migrations.AlterUniqueTogether(
            name='isin',
            unique_together={('movie', 'list')},
        ),
    ]