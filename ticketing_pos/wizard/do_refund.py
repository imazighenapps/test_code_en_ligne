# -*- encoding: utf-8 -*-

from odoo import api, fields, models



class DoRefund(models.TransientModel):
    _name = 'do.refund'
    _description = "Do Refund wizard"
 

    order_id        = fields.Many2one('ticketing.order',"Billet à remboursé")        
    company_id      = fields.Many2one('res.company', default=lambda self: self.env.company, string='Sociétés')
    currency_id     = fields.Many2one('res.currency', string='Devise',related='company_id.currency_id',)
    amount_refund   = fields.Monetary(string='Montant remboursé', readonly=False)
    amount_order    = fields.Monetary(string='Montant du billet', readonly=True)
    note            = fields.Text('Motif de remboursement',required=True)    



    def create_refund(self):
        self.env['refund.order'].create({ 'name'            : self.order_id.name,
                                          'order_id'        :self.order_id.id,                        
                                          'company_id'      : self.company_id.id,    
                                          'currency_id'     : self.currency_id.id,
                                          'amount_refund'   : self.amount_refund,  
                                          'amount_order'    : self.amount_order,
                                          'refund_date'     : fields.Datetime.now(),
                                          'note'            : self.note,
                                                })
        
        self.order_id.order_type = "refund"


