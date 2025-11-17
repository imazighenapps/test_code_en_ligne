# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class TrainStationLine(models.Model):

    _name = 'train.station.line'
     
     
   
    station_id     = fields.Many2one('res.station', string='Gare')
    arrival_time   = fields.Float(string="Heure")
    next_day       = fields.Boolean(string='Le jour suivant')    
    distance       = fields.Float(string="Distance" ,digits=(16, 3))
    sequence       = fields.Integer('Sequence')
    train_id       = fields.Many2one('res.train',string="Train",) 


    