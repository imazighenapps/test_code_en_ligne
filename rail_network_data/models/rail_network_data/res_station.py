# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.modules.module import get_module_resource
import base64

class ResStation(models.Model):

     _name =      'res.station'




     name             =  fields.Char(string="Nom")
     code             =  fields.Char(string="Code")
     name_arabe       =  fields.Char(string="Nom en arabe")
     state_id         =  fields.Many2one('res.country.state',string='wilaya Desservie')
     longitude        =  fields.Float(string='Longitude',digits=(2,10))
     latitude         =  fields.Float(string="latitude",digits=(2,10))
     image            = fields.Image()
     region_id        = fields.Many2one('res.region',string='Région')
     is_bifurcation   = fields.Boolean(string='Est une gare de bifurcation',)   
     bifurcation      = fields.Char('Bifurcation N°')   
     ip               = fields.Char('Adresse IP')
     node_id          = fields.Integer('Node ID')


