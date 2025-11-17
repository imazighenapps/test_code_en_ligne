# -*- coding: utf-8 -*-
{
    'name': "Rail Network Data",
    'summary': """ SmartF """,
    'description': """ Système de Management et d'Automatisation de la Réservation et des Tickets Ferroviaires """,
    'author': "SNTF",
    'website': "https://www.sntf.dz",
    'category': 'ticketing',
    'version': '1.0',
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        
        'views/rail_network_data/res_network.xml',
        'views/rail_network_data/res_station.xml',
        'views/rail_network_data/res_relation.xml',
        'views/rail_network_data/res_branch.xml',
        'views/rail_network_data/res_train.xml',

        'views/price/base_price_kilometer.xml',
        'views/price/scale_pricing.xml',
        'views/price/account_tax_stamp.xml',
        'views/price/traveler_profile.xml',
        'views/configuration/calendar.xml',
        'views/configuration/res_class.xml',
        
        'views/configuration/ticketing_service.xml',
        'views/configuration/traffic_mode.xml',
        'views/configuration/train_type.xml',


        'views/config_file/config_file.xml',


        'menu/menu.xml',
    ],
}
