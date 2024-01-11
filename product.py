# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Id


class Category(metaclass=PoolMeta):
    __name__ = 'product.category'
    category_sequence = fields.Boolean("Category Sequence")
    template_sequence = fields.Many2One('ir.sequence', "Product Sequence",
        domain=[
            ('sequence_type', '=', Id('product', 'sequence_type_template')),
            ],
        states={
            'required': Bool(Eval('category_sequence')),
            },
        help="Used to generate the first part of the product code.")

    @classmethod
    def __register__(cls, module_name):
        table = cls.__table_handler__(module_name)

        # Migration from 5.4: rename product_sequence into template_sequence
        if (table.column_exist('product_sequence')
                and not table.column_exist('template_sequence')):
            table.column_rename('product_sequence', 'template_sequence')
        super(Category, cls).__register__(module_name)

    @classmethod
    def view_attributes(cls):
        return super(Category, cls).view_attributes() + [
            ('/form/notebook/page[@id="category_sequence"]', 'states', {
                    'invisible': ~Eval('category_sequence', False),
                    }),
            ]


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    category_sequence = fields.Many2One('product.category', "Category Sequence",
        domain=[
            ('category_sequence', '=', True),
            ],
        states={
            'readonly': (Bool(Eval('id', -1) >= 0)
                & Bool(Eval('category_sequence', -1))),
        },
        help="Sequence code used to generate the product code.")

    @classmethod
    def _new_category_code(cls, category_id):
        Category = Pool().get('product.category')
        category = Category(category_id)
        sequence = category.template_sequence
        if sequence:
            return sequence.get()

    @classmethod
    def create(cls, vlist):
        vlist = [v.copy() for v in vlist]
        for values in vlist:
            values.setdefault('products', None)
            if not values.get('code') and values.get('category_sequence'):
                category_id = values.get('category_sequence')
                values['code'] = cls._new_category_code(category_id)
        return super().create(vlist)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        to_write = []
        for templates, values in zip(actions, actions):
            if values.get('category_sequence'):
                category_id = values.get('category_sequence')
                for template in templates:
                    values['code'] = cls._new_category_code(category_id)
                    to_write.extend(([template], values))
            else:
                to_write.extend((templates, values))
        super().write(*to_write)


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'
