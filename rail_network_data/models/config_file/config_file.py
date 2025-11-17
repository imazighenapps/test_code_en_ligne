# -*- encoding: utf-8 -*-

from odoo import api, fields, models



class ConfigFile(models.Model):
    _name = 'config.file'
    _description = "Fichier de configuration exporté"
    _order = 'date desc'


    name            = fields.Char("Nom du fichier", required=True, default="config.json")
    date            = fields.Datetime("Date de création", default=lambda self: fields.Datetime.now())
    file_data       = fields.Binary("Fichier JSON", required=True, attachment=True)
    file_filename   = fields.Char("Nom du fichier original", default="config.json")
    description     = fields.Text("Description ou commentaire")
    is_active       = fields.Boolean("Actif", default=True)
    network_id      = fields.Many2one('res.network', string="Réseau")

    