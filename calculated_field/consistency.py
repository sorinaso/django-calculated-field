from collections import namedtuple
import calculated_field

Inconsistency = namedtuple('Inconsistency', 'object field_name database_value calculated_value')

class ConsistencyChecker(object):
    """Clase que chequea la consistencia de los campos calculados."""
    def __init__(self):
        self.inconsistencies = []

        for (model, recalculations) in calculated_field.recalculation.table.iteritems():
            for recalculation in recalculations:
                calculation = recalculation.field_calculation
                objs = calculation.model.objects.all()

                for obj in objs:
                    database_value = getattr(obj, calculation.field_name)
                    calculated_value = calculation.method(obj)

                    if database_value != calculated_value:
                        self.inconsistencies.append(
                            Inconsistency(
                                object=obj,
                                field_name=calculation.field_name,
                                database_value=database_value,
                                calculated_value=calculated_value
                            )
                        )
