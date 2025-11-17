# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import ast
import base64
import json 


class TicketingOrder(models.Model):
    _name = 'ticketing.order'
    _discreption ="Ventes"
    _order = "id desc"
    
  
    name             = fields.Char('N°',default="23102-003-0002000-sntf")
    train1           = fields.Char('Train')
    train2           = fields.Char('Train de correspendance',default="/")
    departure_date   = fields.Date('Date')  
    departure_hour   = fields.Char('Heure')  
    start_station    = fields.Char(string='Gare de départ',)
    end_station      = fields.Char(string="Gare d'arrivée",)
    correspondence   = fields.Char(string='Correspondance',default="/")
    distance         = fields.Float('Distance')
    class_train      = fields.Char(string='Classe')
    company_id       = fields.Many2one('res.company', default=lambda self: self.env.company, string='Sociétés')
    currency_id      = fields.Many2one('res.currency', string='Devise',related='company_id.currency_id',)
    course           = fields.Selection(string='Parcours',selection=[('one_way_ticket', 'Aller simple'),('round_trip', 'Aller/Retour')],default="one_way_ticket")
       
    traveler_profile            =  fields.Char(string='Catégorie tarifaire')
    traveler_profile_with       =  fields.Char(string='Catégorie tarifaire Avec')
    passengers_number           =  fields.Integer(string="Nombre") 
    companion_number            =  fields.Integer(string="Nombre avec")
    passengers_discount         =  fields.Float(string="Réduction") 
    companion_discount          =  fields.Float(string="Réduction Avec") 
    order_type                  =  fields.Selection(string='Type', selection=[('sale', 'Vente'),('booking', 'Réservation'),('working_capital_to_recover', 'Fond de roulement a récupérer'),('working_capital_advance', 'Avance fond de roulement'),('refund', 'Remboursé'),('cancel', 'Annulé')])
    json_order                  =  fields.Text('Json Order')

    amount_untaxed   = fields.Monetary(string='Prix HT',readonly=True)
    amount_tax       = fields.Monetary(string='TVA', readonly=True)
    amount_stamp     = fields.Monetary(string='Timbre', readonly=True )  
    amount_total     = fields.Monetary(string='Total', readonly=True)   

    #related fields
    train1_id                = fields.Many2one('res.train', string='Train')
    train2_id                = fields.Many2one('res.train', string='Train de correspendance')
    start_station_id         = fields.Many2one('res.station', string='Gare de départ',)
    end_station_id           = fields.Many2one('res.station', string="Gare d'arrivée",)
    correspondence_id        = fields.Many2one('res.station', string='Correspondance')
    class_train_id           = fields.Many2one('res.class',string='Classe')
    traveler_profile_id      = fields.Many2one( 'traveler.profile',string='Catégorie tarifaire')
    traveler_profile_with_id =  fields.Many2one('traveler.profile',string='Catégorie tarifaire Avec')
    cancellation_reason      = fields.Text("Motif d'annulation")


    def do_refund(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("ticketing_pos.do_refund_action")
        context = self._context.copy()
        if 'context' in action and isinstance(action['context'], str):
            context.update(ast.literal_eval(action['context']))
        else:
            context.update(action.get('context', {}))
        action['context'] = context
        action['context'].update({
            'default_order_id': self.id,
            'default_amount_order': self.amount_total,

        })

        return action
    

    def create(self, vals):
        _logger.warning('\n ok ok vals =>%s',vals)
        res = super().create(vals)
        json_order = vals['json_order']
        json_order['order_id'] = res.id
        order_file_obj = self.env['order.file'].sudo().search([('date_file','=',fields.Datetime.now())])
        if order_file_obj:
            decoded_json = base64.b64decode(order_file_obj.file_data).decode('utf-8')
            json_data = json.loads(decoded_json)
            json_data["data"].append(json_order)
            json_str = json.dumps(json_data, separators=(",", ":"), ensure_ascii=False)
            encoded_file = base64.b64encode(json_str.encode('utf-8'))
            order_file_obj.file_data = encoded_file
        else:
            data_dict = {'date':vals['departure_date'],'data':[json_order]}     
            json_str = json.dumps(data_dict, separators=(",", ":"), ensure_ascii=False)
            encoded_file = base64.b64encode(json_str.encode('utf-8'))
            self.env['order.file'].create({
                'name': 'ventes',
                'file_data': encoded_file,
                'file_filename': 'vents'+str() +'.json',
                'description': 'Fichier généré automatiquement',
            })


        return res

    def do_cancel_order(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("ticketing_pos.do_cancel_action")
        context = self._context.copy()
        if 'context' in action and isinstance(action['context'], str):
            context.update(ast.literal_eval(action['context']))
        else:
            context.update(action.get('context', {}))
        action['context'] = context
        order_type_label = dict(self._fields['order_type'].selection).get(self.order_type)
        action['context'].update({
            'default_order_id': self.id,
             'default_msg': f"""<div class="alert alert-warning" role="alert" style="font-size:14px; line-height:1.5;">
                                    <h4 class="alert-heading">⚠️ Attention !</h4>
                                    <p>
                                        Vous êtes sur le point d'<strong>annuler</strong> la
                                        <strong>{order_type_label}</strong> <span style="color:#d9534f;">N° {self.name}</span>.
                                    </p>
                                    <hr style="margin:8px 0;">
                                    <p class="mb-0">
                                        Cette action est <strong>irréversible</strong>. Veuillez confirmer votre décision.
                                    </p>
                                </div>
                            """
                             })

        return action