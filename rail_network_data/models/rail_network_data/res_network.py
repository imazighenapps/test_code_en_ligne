# -*- encoding: utf-8 -*-

from odoo import api, fields, models
import base64
import json
import networkx as nx
import logging
_logger = logging.getLogger(__name__)
import matplotlib.pyplot as plt
from zeep import Client
import requests
import random
import cx_Oracle
from datetime import datetime, time




class ResNetwork(models.Model):
    _name = 'res.network'


    name            = fields.Char("Réseau", required=True, default="SNTF") 
   