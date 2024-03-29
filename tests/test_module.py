
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool


class ProductSequenceTestCase(ModuleTestCase):
    'Test ProductSequence module'
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
        cat_pt_sequence, pt_sequence = Sequence.create([{
                    'name': 'Category Product',
                    'sequence_type': product_sequence_type,
                    'prefix': 'CAT-PT',
                    }, {
                    'name': 'Product',
                    'sequence_type': product_sequence_type,
                    'prefix': 'PT',
                    }])
        cat1, = Category.create([{
                    'name': 'Category PT',
                    'category_sequence': True,
                    'template_sequence': cat_pt_sequence,
                    }])
        self.assertTrue(cat1.id)

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

        pt3, pt4 = Template.create([{
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
                    'products': [('create', [{
                                    'description': 'P4',
                                    }])]
                    }])
        self.assertEqual(pt3.code, 'CAT-PT1')
        self.assertEqual(pt3.products[0].suffix_code, None)
        self.assertEqual(pt3.products[0].code, 'CAT-PT1')
        self.assertEqual(pt4.code, 'PT1')
        self.assertEqual(pt4.products[0].suffix_code, None)
        self.assertEqual(pt4.products[0].code, 'PT1')

        Configuration.write([config], {
            'template_sequence': None,
            })
        pt5, = Template.create([{
                    'name': 'P5',
                    'type': 'goods',
                    'default_uom': unit.id,
                    'products': [('create', [{
                                    'description': 'P5',
                                    }])]
                    }])
        self.assertEqual(pt5.products[0].suffix_code, None)
        self.assertEqual(pt5.products[0].code, None)

        Template.write([pt5], {'category_sequence': cat1})
        self.assertEqual(pt5.code, 'CAT-PT2')
        self.assertEqual(pt5.products[0].suffix_code, None)
        self.assertEqual(pt5.products[0].code, 'CAT-PT2')


del ModuleTestCase
