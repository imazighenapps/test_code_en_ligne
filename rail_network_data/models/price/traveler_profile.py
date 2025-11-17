# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from random import randrange
import logging
_logger = logging.getLogger(__name__)



# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class TravelerProfile(models.Model):
    _name = 'traveler.profile'
    _description = 'Profil voyageur'

    


    code               = fields.Char('Code SNTF')
    name               = fields.Char('Catégorie Tarifaire/Profil')
    validity_type      = fields.Selection(string="Type de validité", selection=[('fixed', 'fixée'),('period', 'Période'),('python_code', 'Code Python'),])  
    validity_number    = fields.Float('Validité')   
    validiy_unit       = fields.Selection(string="Unité",selection=[('month', 'mois'),('day', 'jour'),] )
    validity_from      = fields.Datetime('Du')
    validity_to        = fields.Datetime('Au')
    python_validation  = fields.Text('Validation python',default="#8+ distance // 100") 
    class_ids          = fields.Many2many('res.class',string='Classe(s)')     
    over_ranking       = fields.Boolean("Sur-classement")
    path               = fields.Selection(string="Trajet", selection=[('ar', 'AR'),('as', 'AS'),('as_ar', 'AS/AR')])    
    passengers_number_from  = fields.Integer('Nombre de passagers du',default=1)
    passengers_number_to    = fields.Integer('Nombre de passagers au',default=1)
    # category_with_ids   = fields.One2many(comodel_name='traveler.profile.with.line', inverse_name="parent_category_Profil_id", string='Catégorie Avec',)
    is_defaul            = fields.Boolean(string='Est la Catégorie par défaut à la vente',)
    
    note               = fields.Text(string='Note',)
    discount           = fields.Float("Réduction(%)")     
    category           = fields.Selection(string='Catégorie',selection=[('ordinary', 'Ordinaire'), 
                                                                 ('reduced', 'Réduit'), 
                                                                 ('free', 'gratuit') ,
                                                                 ('group', 'Groupe')],default='ordinary')
    category_with_ids = fields.Many2many('traveler.profile','traveler_profile_rel', 'profile_id',  'related_profile_id',                                
                                    string="Catégorie Avec"
                                )


    # class TravelerProfileWithLine(models.Model):
    #     _name = 'traveler.profile.with.line'
    #     _description = 'Profil voyageur avec'



    

    #     parent_category_Profil_id = fields.Many2one('traveler.profile', string='Catégorie Avec')
    #     category_Profil_id = fields.Many2one('traveler.profile', string='Catégorie Avec',)
        