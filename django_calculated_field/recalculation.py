from django.db.models.signals import post_save, post_delete
from django.apps import apps

# Table de dependencias para refrescos.
from django_calculated_field.helpers import find_fks
from django_calculated_field import CalculatedFieldError

table = {}

# modelos Hookeados.
hooked_models = []

def recalculate_all():
    for (cls, frc) in table.items():
        for instance in frc.field_calculation.model.objects.all():
            frc.field_calculation.calculate(instance)

def recalculate_fks(instance, check_contition):
    """Refresca las dependencias de la instancia."""
    if instance.__class__ in table:
        recalculations = set()

        for dep in table[instance.__class__]:
            if not check_contition or dep.must_recalculate(instance):
                recalculations.add(dep.field_calculation)

        for d in recalculations:
            recalculation_target_fks = find_fks(instance.__class__, d.model)

            if not len(recalculation_target_fks) == 1:
                raise CalculatedFieldError("Debe haber una y solo una clave foranea al dependiente "
                                "los fk al dependiente son: %r" % recalculation_target_fks)

            recalculation_target = getattr(instance, recalculation_target_fks[0].name)
            d.calculate(recalculation_target)

def recalculate_fields_if_must(sender, instance, **kwargs):
    recalculate_fks(instance, True)

def recalculate_fields(sender, instance, **kwargs):
    recalculate_fks(instance, False)

class FieldRecalculation(object):
    """
    Clase base de un recalculo del campo.
    """

    @classmethod
    def build(cls, field_calculation, recalculates_on):
        """Construye una dependencia de un diccionario."""
        try:
            model = apps.get_model(*(recalculates_on['model'].split('.')))
        except LookupError:
            raise CalculatedFieldError("No existe el modelo de recalculo: %s" % recalculates_on['model'])

        return FieldRecalculationOnRelated(field_calculation, model,
                                     recalculates_on.get('if_post_save'))

    def must_recalculate(self, instance):
        """ Devuelve si debe recalcular el campo."""
        raise NotImplementedError('Se implementa en las clases de abajo.')
    
class FieldRecalculationOnRelated(object):
    """
    Esta clase depresenta un recalculo del campo por el cambio de un
    modelo relcionado, en el post_save se recalcula si no hay condicion
    o si la condicion del lambda es verdadera en un delete se recalcula
    siempre.

    `field_calculation`:
        Calculo de campo relacionado.
    `model`:
        Modelo del cual depende el calculo.
    `condition`:
        Lambda que recibe que decide si se debe recalculo o no el lambda
        se debe declarar de la siguiente forma:

        lambda i: i.id == 5 or i.status = 'OK'

        donde i es la instanca del modelo que depende que se guarda y el
        lambda se aplica en el postsave.
    """
    def __init__(self, field_calculation, model, condition=None):
        self.field_calculation = field_calculation
        self.model = model
        self.condition = condition

        if not table.has_key(self.model):
            table[self.model] = [self]
        else:
            table[self.model].append(self)

        # Si no esta hookead el modelo(al post_save) lo hookeo y nunca mas.
        if not self.model in hooked_models:
            post_save.connect(recalculate_fields_if_must, sender=self.model,
            dispatch_uid='RecalculateSaveModelDependency-%s' % self.model)

            post_delete.connect(recalculate_fields, sender=self.model,
            dispatch_uid='RecalculateDeleteModelDependency-%s' % self.model)

            hooked_models.append(self.model)

    def must_recalculate(self, instance):
        """ Devuelve si debe recalcular el campo."""
        return self.condition is None or self.condition(instance)