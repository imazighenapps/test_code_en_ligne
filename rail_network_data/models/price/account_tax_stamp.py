# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class AccountTaxStamp(models.Model):
    _name = 'account.tax.stamp'
  

    name            =  fields.Char("Nom")
    stamp_line_ids  = fields.One2many(string='Configuration de calcul de timbre',comodel_name='account.tax.stamp.line',inverse_name='account_tax_id', )
    

        

class AccountTaxStampLine(models.Model):
    _name="account.tax.stamp.line"


    from_dinar          = fields.Float('Du dinar')
    to_dinar            = fields.Float('Au dinar')
    calculation_type    = fields.Selection(string='Type de calcul',selection=[('fixed', 'Fixe'), ('percentage', 'Pourcentage')])
    amount              = fields.Float('Montant')
    account_tax_id      = fields.Many2one(string="Taxe", comodel_name="account.tax.stamp",ondelete="cascade",)