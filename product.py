# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['Configuration', 'Category', 'Template', 'Product']


class Configuration(metaclass=PoolMeta):
    __name__ = 'product.configuration'
    product_sequence = fields.Many2One('ir.sequence', 'Sequence', domain=[
            ('code', '=', 'product.category'),
            # ('company', '=', None),
            ],
        context={
            'code': 'product.category',
            },
        help='Sequence code used to generate the product code.')


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
        depends=['category_sequence'],
        help='Sequence code used to generate the product code.')


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    @classmethod
    def get_product_sequence(cls):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Configuration = pool.get('product.configuration')

        config = Configuration(1)
        if not config.product_sequence:
            return
        return Sequence.get_id(config.product_sequence.id)

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Template = pool.get('product.template')

        for value in vlist:
            code = value.get('code', '')
            if code == '':
                category_sequence = Template(value['template']).category_sequence
                if category_sequence and category_sequence.product_sequence:
                    sequence = Sequence.get_id(
                        category_sequence.product_sequence.id)
                else:
                    sequence = cls.get_product_sequence()
                if sequence:
                    value['code'] = sequence
        return super(Product, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Template = pool.get('product.template')

        actions = iter(args)
        args = []
        for products, values in zip(actions, actions):
            if 'code' in values and values['code'] is not None:
                template = (Template(values['template'])
                    if values.get('template') else None)
                for product in products:
                    category_sequence = (template.category_sequence if template
                        else product.template.category_sequence)
                    new_vals = values.copy()
                    if category_sequence and category_sequence.product_sequence:
                        sequence = Sequence.get_id(
                            category_sequence.product_sequence.id)
                    else:
                        sequence = cls.get_product_sequence()
                    if sequence:
                        new_vals['code'] = sequence
                    args.extend(([product], new_vals))
            else:
                args.extend((products, values))
        super(Product, cls).write(*args)

    @classmethod
    def copy(cls, products, default=None):
        Sequence = Pool().get('ir.sequence')

        if default is None:
            default = {}
        if 'code' in default:
            return super(Product, cls).copy(products, default)

        default = default.copy()
        result = []
        for product in products:
            if product.template.category_sequence \
                    and product.template.category_sequence.product_sequence:
                sequence = Sequence.get_id(
                    product.template.category_sequence.product_sequence.id)
            else:
                sequence = cls.get_product_sequence()
            if sequence:
                default['code'] = sequence
            result += super(Product, cls).copy([product], default)
        return result
