import inspect
from django.db.models.fields import FieldDoesNotExist
from calculated_field import CalculatedFieldError, recalculation
from calculated_field.recalculation import FieldRecalculation
from django.conf import settings
from django.apps import apps

def load_field_calculations_from_settings():
    #if type(recalculation.table) is not dict or len(recalculation.table) != 0:
    #    raise CalculatedFieldError(
    #        "La tabla de recalculos no es un diccionario vacio %r"
    #        % recalculation.table)
    recalculation.table = {}

    ret = []

    try:
        fcds = getattr(settings, "FIELD_CALCULATIONS")
    except AttributeError:
        raise CalculatedFieldError("No esta definida la variable "
                                   "FIELD_CALCULATIONS en los settings")

    for fcd in fcds:
        fc, fr = FieldCalculation.build(fcd)
        ret.append(fc)

    return ret


class FieldCalculation(object):
    """
    Esta clase representa un calculo un campo en la BD.

    `field_name`: Campo en el modelo del metodo.
    `method`: Metodo que hace el calculo en el campo calculado.
    """
    def __init__(self, field_name, method):
        self.field_name = field_name
        self.method = method
        self.model = None

        # Obtengo el modelo del metodo.
        for cls in inspect.getmro(self.method.im_class):
            if self.method.__name__ in cls.__dict__: self.model = cls

        if self.model is None:
            raise CalculatedFieldError('El metodo %r no pertenece a ningun modelo' % self.method)

        try:
            self.model._meta.get_field_by_name(self.field_name)
        except FieldDoesNotExist:
            raise CalculatedFieldError("El campo %s no existe en el modelo %s"
                % (self.field_name, self.model))

    @classmethod
    def build(cls, definition):
        """Contruye un calculo de un campo a partir de su definicion."""
        app_name, model_name, field_name = definition['field'].split('.')

        model = apps.get_model(app_name, model_name)
        method_name = "calculate_%s" % field_name

        try:
            method = getattr(model, method_name)
        except AttributeError:
            raise CalculatedFieldError("El metodo %s no existe en la clase %s" %
                                       (method_name, model))

        fc = FieldCalculation(field_name, method)
        fr = FieldRecalculation.build(fc, definition['recalculates_on'])
        
        return fc, fr

    def calculate(self, instance):
        """Calcula el campo en la base de datos."""
        setattr(instance, self.field_name, self.method(instance))
        instance.save()

  