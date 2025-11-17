# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class UsersPos(models.Model):
    _name = "res.users.pos"

    name           = fields.Char("Nom")
    login          = fields.Char("Login")
    password       = fields.Char("Mot de passe")
    code           = fields.Char("Matricule")
    station_id     = fields.Many2one("res.station","Gare")
    user_id        = fields.Many2one('res.users', string='Utilisateur')
   



    def create(self, vals):
        self.env['res.users'].sudo().create(vals)
        return super().create(vals)
    

    def write(self, vals):
        return super().write(vals)
    

    def unlink(self):
        return super().unlink()