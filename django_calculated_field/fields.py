from django.core.exceptions import FieldError
from django.db import models


class CalculatedFieldMixin(object):
    def init_metadata(self, kwargs):
        for kwarg_key in ('recalculates_on',):
            if not kwargs.has_key(kwarg_key):
                raise FieldError("El campo debe tener seteado el atributo %s" % kwarg_key)

        self.recalculates_on = kwargs['recalculates_on']
        del kwargs['recalculates_on']


class CalculatedDecimalField(models.DecimalField, CalculatedFieldMixin):
    """Campo decimal calculado."""

    description = "Campo decimal calculado."

    def __init__(self, *args, **kwargs):
        self.init_metadata(kwargs)
        super(CalculatedDecimalField, self).__init__(*args, **kwargs)


class CalculatedIntegerField(models.IntegerField, CalculatedFieldMixin):
    """Campo entero calculado."""
    
    description = "Campo entero calculado."

    def __init__(self, *args, **kwargs):
        self.init_metadata(kwargs)
        super(CalculatedIntegerField, self).__init__(*args, **kwargs)
