# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


class Category(metaclass=PoolMeta):
    __name__ = 'product.category'
    category_sequence = fields.Boolean('Category Sequence')
    product_sequence = fields.Many2One('ir.sequence', 'Sequence', domain=[
            ('code', '=', 'product.category'),
            ],
        context={
            'code': 'product.category',
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

    def get_product_sequence(self):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        if self.category_sequence and self.category_sequence.product_sequence:
            return Sequence.get_id(self.category_sequence.product_sequence.id)


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

        if record and not 'code' in values:
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
            values['code'] = new_code
        return values

    @classmethod
    def copy(cls, products, default=None):
        if default is None:
            default = {}
        if 'code' in default:
            return super(Product, cls).copy(products, default)

        default = default.copy()
        result = []
        for product in products:
            sequence = product.template.get_product_sequence()
            if sequence:
                default['code'] = sequence
            result += super(Product, cls).copy([product], default)
        return result
