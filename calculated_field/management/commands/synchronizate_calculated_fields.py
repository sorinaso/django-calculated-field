from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Soncriniza los campos calculados con los valores en la base de datos."""
    def handle(self, *args, **options):
        field_calculations = []

        for calculation in field_calculations:
            for instance in calculation.model.objects.all():
                database_value = getattr(instance, calculation.field_name)
                calculated_value = calculation.method(instance)

                if database_value != calculated_value:
                    self.stdout.write(
                        """
                        El campo %s del objecto(modelo: %s, id: %d) no coincide:
                        base de datos: %r
                        calculado: %r
                        """ % (calculation.field_name, instance.__class__,
                               instance.id, database_value, calculated_value)
                    )