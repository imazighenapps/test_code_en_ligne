# -*- coding: utf-8 -*-
from odoo import models, fields, api



class ResRegion(models.Model):
     _name = 'res.region'


     name              =  fields.Char("Région")
     