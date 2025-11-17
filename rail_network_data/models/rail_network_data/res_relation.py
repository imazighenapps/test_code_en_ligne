# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from random import randrange

class ResRelation(models.Model):
    _name  = 'res.relation'
     
     
    name               = fields.Char('Nom',required=True)
    code               = fields.Char('Code')
    branch_ids        = fields.One2many(string="Gares",comodel_name="relation.branch.line",inverse_name="relation_id",)
    amount_distance    = fields.Float("Longeur de la relation(KM)",compute='_compute_amount_distance')    
  
    @api.depends('branch_ids')
    def _compute_amount_distance(self):
        for rec in self:
            distance = 0
            for line in rec.branch_ids:
                distance += line.distance
            rec.amount_distance = distance




class RelationBranchLine(models.Model):

    _name = 'relation.branch.line'
    _order = 'sequence'
    _rec_name = 'branch_id' 


    branch_id  = fields.Many2one('res.branch', string='Branche', required=True,) 
    distance   = fields.Float(string="Distance d'arrivé" ,digits=(16, 3),related="branch_id.amount_distance")
    sense      = fields.Selection(selection=[('normal', 'Bon sens'), ('reverse', 'Sens inversé')], string='Sens', default='normal',
        required=True,
        help="Indique le sens du trajet : Bon sens ou Sens inversé."
    )
    relation_id           = fields.Many2one(comodel_name='res.relation',string='Relation',ondelete='cascade')
    sequence              = fields.Integer(default=1)


        