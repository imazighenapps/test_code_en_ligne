# -*- encoding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)
import string
from itertools import combinations

class BasePriceKilometer(models.Model):
    _name = 'base.price.kilometer'
    _description = 'Prix de base Kilométrique'


    name                = fields.Char('Nom')
    service_id          = fields.Many2one('ticketing.service',string='Service',)  
    class_ids           = fields.Many2many('res.class', string='Classe(s)',)
    train_type_ids      = fields.Many2many('train.type', string='Type(s) de(s) train(s)',)
    distance_price_ids  = fields.One2many(string="Prix par distances",comodel_name="base.price.kilometer.line",inverse_name="base_price_kilometer_id", )



class BasePriceKilometerLine(models.Model):
    _name = 'base.price.kilometer.line'
    _description = 'Prix de base Kilométrique(distance)'

    start_distance     = fields.Integer('Du kilomètre')
    end_distance       = fields.Integer('Au kilomètre')
    price              = fields.Float('Prix',digits=(16, 5))    
    base_price_kilometer_id  = fields.Many2one(string="Prix de base Kilométrique", comodel_name="base.price.kilometer",)