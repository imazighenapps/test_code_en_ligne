# -*- encoding: utf-8 -*-

from odoo import api, fields, models



class RefundOrder(models.Model):
    _name = 'refund.order'
    _description = "Refund order"
 


    name            = fields.Char("N°")
    order_id        = fields.Many2one('ticketing.order',"Billet remboursé")        
    company_id      = fields.Many2one('res.company', default=lambda self: self.env.company, string='Sociétés')
    currency_id     = fields.Many2one('res.currency', string='Devise',related='company_id.currency_id',)
    amount_refund   = fields.Monetary(string='Montant remboursé', readonly=True)
    amount_order    = fields.Monetary(string='Montant du billet', readonly=True)
    note            = fields.Text('Motif de remboursement')    
    refund_date     = fields.Datetime('Date de remboursement')


    