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
        SequenceType = pool.get('ir.sequence.type')
        Sequence = pool.get('ir.sequence')

        unit, = Uom.search([
                    ('name', '=', 'Unit'),
                    ], limit=1)

        sequence_type, = SequenceType.search([(
                    'name', '=', 'Product Category',
                    )], limit=1)
        category_sequence, = Sequence.create([{
                    'name': 'Category',
                    'sequence_type': sequence_type,
                    'prefix': 'CAT',
                    }])
        sequence_type, = SequenceType.search([(
                    'name', '=', 'Variant',
                    )], limit=1)
        product_sequence, = Sequence.create([{
                    'name': 'Product',
                    'sequence_type': sequence_type,
                    'prefix': 'PROD',
                    }])

        category1, = Category.create([{
                    'name': 'Category 1',
                    'category_sequence': True,
                    'product_sequence': category_sequence,
                    }])
        self.assertTrue(category1.id)

        pt1, pt2 = Template.create([{
                    'name': 'P1',
                    'type': 'goods',
                    'list_price': Decimal(20),
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'suffix_code': 'PT1',
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
        Configuration.write([config], {
            'product_sequence': product_sequence,
            })

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
        self.assertEqual(pt3.products[0].code, 'CAT1')
        self.assertEqual(pt4.products[0].code, 'PROD1')

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductSequenceTestCase))
    return suite
