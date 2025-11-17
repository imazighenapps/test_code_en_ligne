# -*- encoding: utf-8 -*-

from odoo import api, fields, models



class UsersFile(models.Model):
    _name = 'users.file'
    _description = "Fichier des utilisateur exporté"
    _order = 'date_file desc'


    name            = fields.Char("Nom du fichier", required=True, default="users.json")
    date_file       = fields.Datetime("Date de création", default=lambda self: fields.Datetime.now())
    file_data       = fields.Binary("Fichier JSON", required=True, attachment=True)
    file_filename   = fields.Char("Nom du fichier original", default="config.json")
    description     = fields.Text("Description ou commentaire")
    network_id      = fields.Many2one('res.network', string="Réseau")

    