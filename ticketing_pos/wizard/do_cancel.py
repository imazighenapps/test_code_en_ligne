# -*- encoding: utf-8 -*-

from odoo import api, fields, models



class DoRefund(models.TransientModel):
    _name = 'do.cancel'
    _description = "Do Order wizard"
 


    order_id        = fields.Many2one('ticketing.order',"Billet à annulé")        
    note            = fields.Text("Motif d'annulation", required=True)    
    msg             = fields.Html('msg')


    def do_cancel(self):
        self.order_id.order_type = "cancel"
        self.order_id.cancellation_reason = self.note