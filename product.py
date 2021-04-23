# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id


class Category(metaclass=PoolMeta):
    __name__ = 'product.category'
    category_sequence = fields.Boolean('Category Sequence')
    product_sequence = fields.Many2One('ir.sequence', 'Sequence', domain=[
            ('sequence_type', '=', Id('product_sequence',
                    'sequence_type_product_category')),
            ],
        context={
            'sequence_type': Id('product_sequence',
                'sequence_type_product_category'),
            },
        states={
            'required': Eval('category_sequence', False),
            },
        depends=['category_sequence'],
        help='Sequence code used to generate the product code.')

    @classmethod
    def __setup__(cls):
        super(Category, cls).__setup__()
        if hasattr(cls, 'accounting'):
            cls.product_sequence.domain.append(('company', '=', None))

    @classmethod
    def view_attributes(cls):
        return super(Category, cls).view_attributes() + [
            ('/form/notebook/page[@id="category_sequence"]', 'states', {
                    'invisible': ~Eval('category_sequence', False),
                    }),
            ]


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    category_sequence = fields.Many2One('product.category', 'Sequence',
        domain=[
            ('category_sequence', '=', True),
            ],
        depends=['category_sequence', 'id'],
        help='Sequence code used to generate the product code.')

    @classmethod
    def write(cls, *args):
        pool = Pool()
        Product = pool.get('product.product')

        actions = iter(args)
        to_update = []
        for templates, values in zip(actions, actions):
            if 'category_sequence' in values:
                to_update += templates
        super().write(*args)

        to_write = []
        for template in templates:
            for product in template.products:
                values = Product.update_code({}, product)
                if values:
                    to_write.append([product])
                    to_write.append(values)
        if to_write:
            Product.write(*to_write)

    def get_product_sequence(self):
        if self.category_sequence and self.category_sequence.product_sequence:
            return self.category_sequence.product_sequence.get()


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    @classmethod
    def create(cls, vlist):
        for values in vlist:
            values.update(cls.update_code(values))
        return super(Product, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        args = []
        for products, values in zip(actions, actions):
            for product in products:
                args.append([product])
                args.append(cls.update_code(values, product))
        super(Product, cls).write(*args)

    @classmethod
    def update_code(cls, values, record=None):
        pool = Pool()
        Template = pool.get('product.template')

        if values.get('suffix_code'):
            return values

        if record and record.suffix_code:
            return values

        if not 'template' in values:
            if not record:
                return values
            template = record.template
        else:
            template = Template(values['template'])

        values = values.copy()
        new_code = template.get_product_sequence()
        if new_code:
            values['suffix_code'] = new_code
        return values

    @classmethod
    def copy(cls, products, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('suffix_code', None)
        return super().copy(products, default=default)
