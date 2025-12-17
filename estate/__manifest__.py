{
    'name': "estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Alejandro López Domínguez",
    'category': 'Real Estate',
    'description': """
    Este es un modulo de prueba para el tutorial de Odoo 19.
    Gestion de Inmobiliaria.
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_menus.xml',
        'views/estate_property_main_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/users_inherited_views.xml'
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3'
}