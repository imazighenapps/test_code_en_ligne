# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from datetime import date, timedelta
import time

class trainCalendar(models.Model):
    _name = 'train.calendar'
    _description = "Calendrier de circulation des trains"

   

    name        = fields.Char("Nom", required=True)
    monday      = fields.Boolean("Lundi")
    tuesday     = fields.Boolean("Mardi")
    wednesday   = fields.Boolean("Mercredi")
    thursday    = fields.Boolean("Jeudi")
    friday      = fields.Boolean("Vendredi")
    saturday    = fields.Boolean("Samedi")
    sunday      = fields.Boolean("Dimanche")
    start_date  = fields.Date("Date de début")
    end_date    = fields.Date("Date de fin")
    exception_dates_ids = fields.One2many("calendar.exception", "calendar_id", "Exceptions")


class TrainCalendarException(models.Model):
    _name = "calendar.exception"
    _description = "Exceptions du calendrier"

    calendar_id = fields.Many2one("train.calendar", required=True)
    date        = fields.Date("Date d'exception", required=True)
    note        = fields.Text("Note")
