# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from random import randrange
import logging
_logger = logging.getLogger(__name__)

class ScaleCalculation(models.Model):
    _name = 'scale.calculation'
    _description = 'Calcul du barème'

    
    start_distance     = fields.Integer('Du kilomètre')
    end_distance       = fields.Integer('Au kilomètre')
    charging_distance  = fields.Float('Distance de taxation') 
    pbk                = fields.Float('PBK',digits=(16, 5)) 
    amount_untaxed     = fields.Float('Prix HT')
    amount_stamp       = fields.Float('Montant du timbre')
    amount_total       = fields.Float('Total sans timbre')  
    full_price         = fields.Float('Plein tarif') 
    scale_pricing_id   = fields.Many2one(string="Barème",comodel_name="scale.pricing",ondelete='cascade')   
    
    @api.onchange('pbk')
    def onchange_pbk(self):
        if self.pbk!=0:
            self.amount_untaxed = self.pbk * self.charging_distance
            self.amount_total =   self.amount_untaxed + self.scale_pricing_id.compute_tva(self.amount_untaxed)
            self.amount_stamp = self.scale_pricing_id.compute_tax_stamp(self.amount_total) 
            self.full_price = self.scale_pricing_id.round_full_price(self.amount_total + self.amount_stamp)
          
          


class DistanceLevelSetting(models.Model):
    _name = 'distance.level.setting'
    _description = 'Paramétrage palier de distance'



    start_distance     = fields.Integer('Du kilomètre')
    end_distance       = fields.Integer('Au kilomètre')
    calculation_basis  = fields.Integer('Base de calcul') 
    scale_pricing_id   = fields.Many2one(string="Barème",comodel_name="scale.pricing",ondelete='cascade')   


class ScalePricing(models.Model):
    _name = 'scale.pricing'
    _description = 'Barème des prix de transport'


    name                  = fields.Char('Barème')
    minimum_perception    = fields.Float('Minimum de perception')
    class_ids             = fields.Many2many('res.class', string='Classe(s)',)
    service_id            = fields.Many2one('ticketing.service',related='base_price_kilometer_id.service_id', string='Service',)  
    train_type_ids        = fields.Many2many('train.type',related='base_price_kilometer_id.train_type_ids', string='Type de train',)

    distance_level_setting_ids = fields.One2many(string="Paramétrage palier de distance", comodel_name="distance.level.setting",inverse_name="scale_pricing_id",)
    scale_calculation_ids      = fields.One2many(string="Calcul du barème", comodel_name="scale.calculation",inverse_name="scale_pricing_id",)
    base_price_kilometer_id    = fields.Many2one( string='Prix de base Kilométrique',comodel_name='base.price.kilometer',)
    tax                        = fields.Float(string='Taxes(%)',default=9)
  
    
    def get_calculated_price(self):
        x=y=step=0
        vals= []
        data = []
        self.scale_calculation_ids = False
        for line in self.distance_level_setting_ids:
            if line.end_distance != 0 and line.calculation_basis != 0:
                step = line.calculation_basis
                tab = list(range(line.start_distance,line.end_distance))
                i = line.start_distance
                while i>= line.start_distance and i <= line.end_distance and  line.end_distance >= i+step: 
                    prices = self.get_full_price(distance=(i+i+step)/2,w=line.calculation_basis) 
                    vals.append({'start_distance':i,
                                'end_distance':i+step,
                                'charging_distance':(i+i+step)/2 ,
                                'pbk':self.get_pbk((i+i+step)/2) ,
                                'amount_untaxed' :  prices[0],
                                'amount_total' :prices[1],
                                'amount_stamp' :prices[2],
                                'full_price': prices[3],
                                                })                    
                    i+=step+1

        for v in vals:
            data.append((0,0,v))           
        self.scale_calculation_ids = data

    #to compute tax stamp form the price 
    def compute_tax_stamp(self,amount):
        amount_stamp = 0
        stamp_id = self.env['account.tax.stamp'].search([],limit=1)
        if stamp_id.id :
           for line in  stamp_id.stamp_line_ids:
               if line.from_dinar <= amount <= line.to_dinar: 
                  if line.calculation_type=='fixed':
                      amount_stamp = line.amount
                  elif line.calculation_type=='percentage' :
                       amount_stamp =  amount * (line.amount/100)
        return amount_stamp    
         

    def compute_tva(self,price):
        amount_tax =price * (self.tax/100)
        return amount_tax

    def get_pbk(self,distance):
        pbk = 0 
        line = self.get_cherched_line(distance)
        if  line.start_distance <= distance <= line.end_distance :
            if distance <= line.end_distance or line.end_distance == -1: 
                pbk = line.price
        return pbk


    def get_cherched_line(self,distance):
        vals=[]
        vals.append(0)
        ln=()
        for line in self.base_price_kilometer_id.distance_price_ids:
            if line.start_distance <= distance <= line.end_distance: 
                ln = line
                vals[0] = ((distance - line.start_distance) + (line.end_distance - distance)) 
                if(distance - line.start_distance) + (line.end_distance - distance) <=  vals[0]:
                    vals[0]=(distance - line.start_distance) + (line.end_distance - distance)    
                    ln = line
        return ln

    def get_full_price(self,distance,w):
        d = distance #int(distance/w)*w+(w-1)/2
        round_net_price = 0
        line  = self.get_cherched_line(d)
        if  line.start_distance <= d <= line.end_distance :
            price = line.price * d  
            tva = self.compute_tva(price)
            stamp = self.compute_tax_stamp(price+tva)
            net_price = round(price + tva + stamp, 0) 
           
            round_net_price = self.round_full_price(net_price)

        return [price,price+tva,stamp, round_net_price]

   
    def round_full_price(self,price):
        round_price = 0 
        div_price = price // 10
        if int(price - (div_price*10)) in [1,2]:
            round_price = div_price * 10 
        elif int(price - (div_price*10)) in [3,4]:
            round_price = div_price * 10 + 5
        elif int(price - (div_price*10)) in [6,7]:
            round_price = div_price * 10 + 5
        elif int(price - (div_price*10)) in [8,9]:
            round_price = div_price * 10 + 10  
        elif int(price - (div_price*10))==5:
            round_price = div_price * 10 + 5  
        else : 
            round_price = div_price * 10   

        if round_price<self.minimum_perception:
            round_price = self.minimum_perception  

        return round_price


