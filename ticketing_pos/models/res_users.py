# -*- coding: utf-8 -*-

from odoo import models, fields, api



class Users(models.Model):
    _inherit = "res.users"

    shortcut_ids = fields.One2many("res.users.shortcuts","user_id",string="Raccourcis")
    code         = fields.Char("Matricule")
    


class UsersShortcuts(models.Model):
    _name = "res.users.shortcuts"


    id_station      = fields.Integer('ID de la gare')
    station_name    = fields.Char('Nom de la gare')
    shortcut        = fields.Char('Raccourci')
    user_id         = fields.Many2one('res.users', string='Utilisateur')

