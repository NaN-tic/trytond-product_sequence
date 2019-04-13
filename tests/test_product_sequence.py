# This file is part of the product_sequence module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool


class ProductSequenceTestCase(ModuleTestCase):
    'Test Product Sequence module'
    module = 'product_sequence'

    @with_transaction()
    def test_product_code(self):
        'Create a product sequence code'
        pool = Pool()
        Uom = pool.get('product.uom')
        Configuration = pool.get('product.configuration')
        Template = pool.get('product.template')
        Category = pool.get('product.category')
        Sequence = pool.get('ir.sequence')

        unit, = Uom.search([
                    ('name', '=', 'Unit'),
                    ], limit=1)

        Sequence.create([{
                    'name': 'PROD',
                    'code': 'product.category',
                    'prefix': 'PROD',
                    }])
        sequence1, sequence2 = Sequence.search([
            ('code', '=', 'product.category')])

        category1, = Category.create([{
                    'name': 'Category 1',
                    'category_sequence': True,
                    'product_sequence': sequence1,
                    }])
        self.assertTrue(category1.id)

        pt1, pt2 = Template.create([{
                    'name': 'P1',
                    'type': 'goods',
                    'list_price': Decimal(20),
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'code': 'PT1',
                                    }])]
                    }, {
                    'name': 'P2',
                    'type': 'goods',
                    'list_price': Decimal(20),
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'description': 'P2',
                                    }])]
                    }])
        self.assertEqual(pt1.products[0].code, 'PT1')
        self.assertEqual(pt2.products[0].code, None)

        config = Configuration(1)
        Configuration.write([config], {'product_sequence': sequence2})

        pt3, pt4 = Template.create([{
                    'name': 'P3',
                    'type': 'goods',
                    'list_price': Decimal(20),
                    'default_uom': unit.id,
                    'category_sequence': category1,
                    'products': [('create', [{
                                    'description': 'P3',
                                    }])]
                    }, {
                    'name': 'P4',
                    'type': 'goods',
                    'list_price': Decimal(20),
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'description': 'P4',
                                    }])]
                    }])
        self.assertEqual(pt3.products[0].code, '1')
        self.assertEqual(pt4.products[0].code, 'PROD1')

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductSequenceTestCase))
    return suite
