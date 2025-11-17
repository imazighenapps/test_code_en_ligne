
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResBranch(models.Model):

     _name = 'res.branch'


     name               = fields.Char('Nom',)#compute='compute_name',
     code               = fields.Char('Code')
     station_line_ids   = fields.One2many(string="Gares",comodel_name="branch.station.line",inverse_name="branch_id", ondelete='cascade')
     amount_distance    = fields.Float("Parcours(KM)")    
     
     def do_nothing(self):
        pass

     @api.onchange("station_line_ids")
     def onchange_station_line_ids(self):
          self.name=""
          self.amount_distance = 0
          sequence = 0
          if len(self.station_line_ids)>=2:
               if self.station_line_ids[0].station_id.name and self.station_line_ids[-1].station_id.name:
                    self.name = self.station_line_ids[0].station_id.name+" ==> "+self.station_line_ids[-1].station_id.name
      
          for line in self.station_line_ids:
               self.amount_distance += line.distance
     
              


     
class BranchStationLine(models.Model):

    _name = 'branch.station.line'
    _order = 'sequence' 
    _rec_name = 'station_id'

             
    station_id         = fields.Many2one('res.station', string='Gare', required=True,) 
    distance           = fields.Float(string="Distance" ,digits=(16, 3))
    branch_id          = fields.Many2one(comodel_name='res.branch',string='Branche',required=False,ondelete='cascade')
    sequence           = fields.Integer('Sequence')




        

 