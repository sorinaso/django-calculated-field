"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.db import models
from django.db.models.aggregates import Sum
from django.test import TestCase
import mock
from django_calculated_field import recalculation, consistency
from django_calculated_field.calculation import FieldCalculation
from django_calculated_field.fields import CalculatedDecimalField, CalculatedIntegerField
from django_calculated_field import CalculatedFieldError
from django_calculated_field.recalculation import FieldRecalculation, FieldRecalculationOnRelated

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

class FieldCalculationTest(TestCase):
    def test_build(self):
        fc, fr = FieldCalculation.build(
            {
            'field': 'django_calculated_field.TestModel.total',
            'recalculates_on': {  'model': 'django_calculated_field.TestModelDependency',
                                  'if_post_save': lambda i: i.status == 'C'}
            },
        )
        
        self.assertEqual(fc.model, TestModel)
        self.assertEqual(fc.field_name, 'total')
        self.assertEqual(fc.method, TestModel.calculate_total)

        
    def test_bad_field(self):
        self.assertRaises(CalculatedFieldError, FieldCalculation, field_name="test_int",
                          method=TestModel.calculate_total)

class FieldRecalculationTest(TestCase):
    def test_build(self):
        condition = lambda i: True
        ret = FieldRecalculation.build(mock.MagicMock(), {'model': 'django_calculated_field.TestModelDependency',
                                                          'if_post_save': condition })
        self.assertIsInstance(ret, FieldRecalculationOnRelated)
        self.assertEqual(ret.model, TestModelDependency)
        self.assertEqual(ret.condition, condition)
        self.assertRaises(CalculatedFieldError,
            FieldRecalculation.build, mock.MagicMock(),
            {'model': 'fruta.NotAModel', 'if_post_save': lambda i: True })


class FieldRecalculationOnRelatedTest(TestCase):
    def setUp(self):
        recalculation.table = {}

    def recalculated_tm(self, tm):
        return TestModel.objects.get(pk=tm.pk)

    def test_table(self):
        self.assertDictEqual(recalculation.table, {})
        ret = FieldRecalculationOnRelated(mock.MagicMock(), TestModelDependency, lambda x: True)
        self.assertDictEqual(recalculation.table, {TestModelDependency: [ret]})
        ret2 = FieldRecalculationOnRelated(mock.MagicMock(), TestModelDependency, lambda x: True)
        self.assertDictEqual(recalculation.table, {TestModelDependency  : [ret, ret2]})

    def test_unconditional_recalculation(self):
        fc = FieldCalculation('total', TestModel.calculate_total)
        dep = FieldRecalculationOnRelated(fc, TestModelDependency)
        tm = TestModel.objects.create()
        self.assertEqual(self.recalculated_tm(tm).total, 0)
        tmd = TestModelDependency.objects.create(dependient=tm, amount=3)
        self.assertEqual(self.recalculated_tm(tm).total, 3)
        tmd = TestModelDependency.objects.create(dependient=tm, amount=4)
        tmd = TestModelDependency.objects.create(dependient=tm, amount=5)
        self.assertEqual(self.recalculated_tm(tm).total, 12)
        TestModelDependency.objects.filter(pk__in=[1,2]).delete()
        self.assertEqual(self.recalculated_tm(tm).total, 5)

    def test_conditional_recalculation(self):
        fc = FieldCalculation('total', TestModel.calculate_total)
        dep = FieldRecalculationOnRelated(fc, TestModelDependency, lambda i: i.must_recalculate)
        tm = TestModel.objects.create()
        self.assertEqual(self.recalculated_tm(tm).total, 0)
        tmd = TestModelDependency.objects.create(dependient=tm, amount=3)
        self.assertEqual(self.recalculated_tm(tm).total, 0)
        tmd = TestModelDependency.objects.create(dependient=tm, amount=3, must_recalculate=True)
        self.assertEqual(self.recalculated_tm(tm).total, 6)
        tmd = TestModelDependency.objects.create(dependient=tm, amount=3, must_recalculate=True)
        self.assertEqual(self.recalculated_tm(tm).total, 9)
        TestModelDependency.objects.filter(pk__in=[1,2]).delete()
        self.assertEqual(self.recalculated_tm(tm).total, 3)

    def test_inconsistency_checker(self):
        fc = FieldCalculation('total', TestModel.calculate_total)
        frc = FieldRecalculationOnRelated(fc, TestModelDependency)
        fc2 = FieldCalculation('total2', TestModel.calculate_total2)
        frc2 = FieldRecalculationOnRelated(fc2, TestModelDependency)
        recalculation.table = { TestModelDependency: [frc, frc2] }

        inconsistencies = []

        tm = TestModel.objects.create()
        tmd = TestModelDependency.objects.create(dependient=tm, amount=3)
        self.assertEquals(consistency.ConsistencyChecker().inconsistencies, inconsistencies)

        tm.total = 9999
        tm.save()

        inconsistencies.append(
        consistency.Inconsistency(
            object=tm,
            field_name="total",
            database_value = tm.total,
            calculated_value = tm.calculate_total()
            )
        )

        self.assertItemsEqual(consistency.ConsistencyChecker().inconsistencies, inconsistencies)

        tm.total2 = 9999
        tm.save()

        inconsistencies.append(
        consistency.Inconsistency(
            object=tm,
            field_name="total2",
            database_value = tm.total2,
            calculated_value = tm.calculate_total2()
            )
        )

        self.assertItemsEqual(consistency.ConsistencyChecker().inconsistencies, inconsistencies)

        tm2 = TestModel.objects.create()
        tmd2 = TestModelDependency.objects.create(dependient=tm2, amount=3)
        tm2.total = 9999
        tm2.save()

        inconsistencies.append(
        consistency.Inconsistency(
            object=tm2,
            field_name="total",
            database_value = tm2.total,
            calculated_value = tm2.calculate_total()
            )
        )

        self.assertItemsEqual(consistency.ConsistencyChecker().inconsistencies, inconsistencies)

        tm2.total2 = 9999
        tm2.save()

        inconsistencies.append(
        consistency.Inconsistency(
            object=tm2,
            field_name="total2",
            database_value = tm2.total2,
            calculated_value = tm2.calculate_total2()
            )
        )

        self.assertItemsEqual(consistency.ConsistencyChecker().inconsistencies, inconsistencies)
