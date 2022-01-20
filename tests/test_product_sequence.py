# This file is part of the product_sequence module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
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

        product_sequence_type, = SequenceType.search([(
                    'name', '=', 'Product',
                    )], limit=1)
        variant_sequence_type, = SequenceType.search([(
                    'name', '=', 'Variant',
                    )], limit=1)
        cat_pt_sequence, cat_pp_sequence, pt_sequence = Sequence.create([{
                    'name': 'Category Product',
                    'sequence_type': product_sequence_type,
                    'prefix': 'CAT-PT',
                    }, {
                    'name': 'Category Variant',
                    'sequence_type': variant_sequence_type,
                    'prefix': 'CAT-PP',
                    }, {
                    'name': 'Product',
                    'sequence_type': product_sequence_type,
                    'prefix': 'PT',
                    }])
        cat1, cat2, = Category.create([{
                    'name': 'Category PP-PT',
                    'category_sequence': True,
                    'product_sequence': cat_pp_sequence,
                    'template_sequence': cat_pt_sequence,
                    }, {
                    'name': 'Category PT',
                    'category_sequence': True,
                    'template_sequence': cat_pt_sequence,
                    }])
        self.assertTrue(cat1.id)
        self.assertTrue(cat2.id)

        pt1, pt2 = Template.create([{
                    'name': 'P1',
                    'type': 'goods',
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'suffix_code': 'F1',
                                    }])]
                    }, {
                    'name': 'P2',
                    'type': 'goods',
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'description': 'P2',
                                    }])]
                    }])
        self.assertEqual(pt1.products[0].code, 'F1')
        self.assertEqual(pt2.products[0].code, None)

        config = Configuration(1)
        Configuration.write([config], {
            'template_sequence': pt_sequence,
            })

        pt3, pt4, pt5 = Template.create([{
                    'name': 'P3',
                    'type': 'goods',
                    'default_uom': unit.id,
                    'category_sequence': cat1,
                    'products': [('create', [{
                                    'description': 'P3',
                                    }])]
                    }, {
                    'name': 'P4',
                    'type': 'goods',
                    'default_uom': unit.id,
                    'category_sequence': cat2,
                    'products': [('create', [{
                                    'description': 'P4',
                                    }])]
                    }, {
                    'name': 'P5',
                    'type': 'goods',
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'description': 'P5',
                                    }])]
                    }])
        self.assertEqual(pt3.code, 'CAT-PT1')
        self.assertEqual(pt3.products[0].suffix_code, 'CAT-PP1')
        self.assertEqual(pt3.products[0].code, 'CAT-PT1CAT-PP1')
        self.assertEqual(pt4.code, 'CAT-PT2')
        self.assertEqual(pt4.products[0].suffix_code, None)
        self.assertEqual(pt4.products[0].code, 'CAT-PT2')
        self.assertEqual(pt5.code, 'PT1')
        self.assertEqual(pt5.products[0].suffix_code, None)
        self.assertEqual(pt5.products[0].code, 'PT1')

        Configuration.write([config], {
            'template_sequence': None,
            })
        pt6, = Template.create([{
                    'name': 'P6',
                    'type': 'goods',
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'description': 'P6',
                                    }])]
                    }])
        self.assertEqual(pt6.products[0].suffix_code, None)
        self.assertEqual(pt6.products[0].code, None)

        Template.write([pt6], {'category_sequence': cat1})
        self.assertEqual(pt6.code, 'CAT-PT3')
        self.assertEqual(pt6.products[0].suffix_code, 'CAT-PP2')
        self.assertEqual(pt6.products[0].code, 'CAT-PT3CAT-PP2')

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductSequenceTestCase))
    return suite
