# -*- coding: utf-8 -*-
{
    'name': "Ticketing POS",

    'summary': """  """,

    'description': """
        
    """,

    'author': "Farid SLIMANI",
    'website': "",
    'license': 'LGPL-3',
    'currency': 'EUR',
    'category': 'Tools',
    'version': '1.0',

    'depends': ['rail_network_data'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/pos.xml',
        'views/res_users.xml',
        'views/ticketing_order.xml',
        'views/refund_order.xml',
        'views/order_file.xml',
        'views/res_users_pos.xml',

        'wizard/do_refund.xml',
        'wizard/do_cancel.xml',
        
       
        'menu/menu.xml',
       
  
    ],
    
    "assets": {
       
        "web.assets_backend": [
            'ticketing_pos/static/src/components/**/*.js',
            'ticketing_pos/static/src/components/**/*.css',
            'ticketing_pos/static/src/components/**/*.xml',
        ],
       
    },


    
}
