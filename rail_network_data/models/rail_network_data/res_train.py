# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

from datetime import date


class TrafficMode(models.Model):
     _name = 'traffic.mode'

     name       = fields.Char("Mode de circulation", required=True )




class TrainType(models.Model):
     _name = 'train.type'

     name  =  fields.Char("Type de train",required=True )  


class TicketingService(models.Model):
     _name = 'ticketing.service'

     name              =  fields.Char("Service",required=True )
     class_ids         =  fields.Many2many('res.class', string='Classe(s)',)

class ResClass(models.Model):
     _name = 'res.class'

     name           =  fields.Char("Classe",required=True )
     is_default     =  fields.Boolean(string='Classe par défaut',)
     
     

class ResTrain(models.Model):

     _name  = 'res.train'

     name                = fields.Char(string="Numéro de train")
     code                = fields.Char(string="Code")
     train_type_id       = fields.Many2one('train.type',string="Type de train")   
     traffic_mode_id     = fields.Many2one('traffic.mode',string='Mode de circulation') 
     start_station_id    = fields.Many2one('res.station',string='Gare de départ',)
     end_station_id      = fields.Many2one('res.station',string="gare d'arrivée",)
     
     departure_time      = fields.Float(string="Heure de départ")
     arrival_time        = fields.Float(string="Heure d'arriveé")
     state               = fields.Selection(string="Etat", selection=[('active', 'En circulation'), ('disable', 'Supprimé de la circulation'), ], default="active",)  
     start_up_dates      = fields.Date(string='Date de mise en service ')     
     amount_distance     = fields.Float("Parcours (KM)")    
     duration            = fields.Float("Durée",)     
     meaning             = fields.Selection([("go", "Aller"),("return","Retour")],string="Sens",default="go")      
     nature              = fields.Char(string="Nature")
     service_id          = fields.Many2one('ticketing.service',string='Service',)  
     class_ids           = fields.Many2many('res.class', string='Classe',)
     scale_pricing_id    = fields.Many2one('scale.pricing', string='Barème')

     date_from         = fields.Date(string='date de', default=fields.Datetime.now,required=True)
     date_to           = fields.Date(string='date à',default='2050-01-01',required=True)
    
     relation_id         = fields.Many2one(string="Relation",comodel_name="res.relation")     
     station_line_ids    = fields.One2many(string="Gares",comodel_name="train.station.line",inverse_name="train_id")
     calendar_id         = fields.Many2one('train.calendar', string='Calendrier',) 
     branch_groupid        = fields.Integer('Branch Group Id')
    

     def do_nothing(self):
          pass

     @api.onchange('relation_id','meaning')
     def _onchange_relation_id(self):
          station_ids = []
          line_data=[]
          lines = []
          self.station_line_ids = False
          distance = 0
          # for branch_line in self.relation_id.branch_ids:
          #      for line in branch_line.branch_id:
          #          for station_line in line.station_line_ids:
          #                if station_line.station_id not in station_ids:
          #                     distance+=station_line.distance
          #                     station_ids.append(station_line.station_id)
          #                     line_data.append((station_line.station_id,distance))
          

                    
          # if self.meaning =='go':
          #      for s in line_data:
          #           lines.append((0, 0, {
          #                'station_id': s[0].id,
          #                'distance': s[1],
          #                }))
                    
          # if self.meaning == 'return':
          #      y =   0
          #      for i in range(len(line_data)-1, -1, -1):
          #           dis = line_data[i+y][1] - line_data[i][1]
          #           y+=1
          #           lines.append((0, 0, {
          #                'station_id': line_data[i][0].id,
          #                'distance': dis
          #                }))
          # self.station_line_ids = lines
