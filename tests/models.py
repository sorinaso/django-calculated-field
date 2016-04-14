from django.db import models
from django.db.models.aggregates import Sum

class TestModel(models.Model):
    total = models.IntegerField(default=0)
    total2 = models.IntegerField(default=0)

    def calculate_total(self):
        return TestModelDependency.objects.filter(dependient=self).\
                aggregate(Sum('amount'))['amount__sum'] or 0

    def calculate_total2(self):
        return (TestModelDependency.objects.filter(dependient=self).
                aggregate(Sum('amount'))['amount__sum'] or 0) * 2

    def __unicode__(self):
        return "TestModel id: %s" % unicode(self.id)

class TestModelDependency(models.Model):
    must_recalculate = models.BooleanField(default=False)
    amount = models.IntegerField()
    dependient = models.ForeignKey(TestModel, related_name='dependencies')
