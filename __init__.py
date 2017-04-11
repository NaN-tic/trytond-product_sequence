# This file is part product_sequence module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import product


def register():
    Pool.register(
        product.Configuration,
        product.Category,
        product.Template,
        product.Product,
        module='product_sequence', type_='model')
