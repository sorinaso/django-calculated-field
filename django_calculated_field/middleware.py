from django.core.exceptions import MiddlewareNotUsed
from django_calculated_field import calculation

class CalculatedFieldMiddleware(object):
    calculated_field_loaded = False

    def __init__(self):
        if not self.calculated_field_loaded:
            calculation.load_field_calculations_from_settings()
            self.calculated_field_loaded = True

        raise MiddlewareNotUsed
        