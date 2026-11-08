
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('negocio', '0001_initial'),
        ('operaciones', '0014_remove_tarima_ck_tarima_capacidad_50_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # No ejecutar eliminaciones físicas: las restricciones
            # ya no existen en la base de datos.
            database_operations=[],

            # Sincronizar el estado histórico de Django.
            state_operations=[
                migrations.RemoveConstraint(
                    model_name='productoempaque',
                    name='ck_producto_precio_no_negativo',
                ),
                migrations.RemoveConstraint(
                    model_name='productoempaque',
                    name='ck_producto_precio_mayor_costo',
                ),
                migrations.RemoveConstraint(
                    model_name='tarima',
                    name='ck_tarima_capacidad_50',
                ),
            ],
        ),

        # Agregar la relación con la operación comercial.
        migrations.AddField(
            model_name='tarima',
            name='operacion_comercial',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tarimas',
                to='negocio.operacioncomercial',
                verbose_name='Operación comercial',
            ),
        ),
    ]
