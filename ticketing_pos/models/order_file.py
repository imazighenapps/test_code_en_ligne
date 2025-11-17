# -*- encoding: utf-8 -*-

from odoo import api, fields, models



class OrderFile(models.Model):
    _name = 'order.file'
    _description = "Fichier de des ventes"
    _order = 'date_file desc'


    name            = fields.Char("Nom du fichier", required=True, default="config.json")
    date_file       = fields.Date("Date", default=lambda self: fields.Datetime.now())
    file_data       = fields.Binary("Fichier JSON", required=True, attachment=True)
    file_filename   = fields.Char("Nom du fichier original", default="config.json")
    description     = fields.Text("Description ou commentaire")
    network_id      = fields.Many2one('res.network', string="Réseau")
    synced          = fields.Boolean("Synchronisé", default=False)