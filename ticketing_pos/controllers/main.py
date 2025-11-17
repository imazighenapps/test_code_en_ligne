# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models
from odoo.addons.mail.controllers.mail import MailController
from odoo import http
from odoo.http import request
import base64
import json 
import reportlab
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image

import qrcode
from reportlab.lib.utils import ImageReader


_logger = logging.getLogger(__name__)


class TicketingPosController(http.Controller):

    @http.route('/lead/data', type='json', auth='user', methods=['POST'])
    def load_data(self):
        latest_config = request.env['config.file'].sudo().search([('is_active','=',True)], order='date desc', limit=1)
        if not latest_config or not latest_config.file_data:
            return {'error': 'Aucun fichier de configuration disponible.'}
        try:
            decoded_json = base64.b64decode(latest_config.file_data).decode('utf-8')
            json_data = json.loads(decoded_json)
        except Exception as e:
            return {'error': 'Erreur lors de la lecture du fichier JSON.', 'details': str(e)}
        return json_data
    

    @http.route('/shortcut/save', type='json', auth='user')
    def save_shortcut(self, shortcuts):
        user = request.env.user
        Shortcut = request.env['res.users.shortcuts'].sudo()
        Shortcut.search([('user_id', '=', user.id)]).unlink()
        for s in shortcuts:
            Shortcut.create({
                'id_station': s.get('station_id'),
                'station_name': s.get('station_name'),
                'shortcut': s.get('shortcut'),
                'user_id': user.id,
            })
        return {"status": "ok"}


    @http.route('/shortcut/load', type='json', auth='user')
    def load_shortcut(self):
        user = request.env.user
        Shortcut = request.env['res.users.shortcuts'].sudo()
        records = Shortcut.search([('user_id', '=', user.id)])

        result = [{
            'id': r.id,
            'station_id': r.id_station,
            'station_name': r.station_name,
            'shortcut': r.shortcut,
        } for r in records]

        return result
    
    @http.route('/save/order', type='json', auth='user')
    def save_order(self, **data):

        order_data = data['params']
        departure_hour = self.get_float_hour_from_string(order_data['selectedTrains']['trains'][0]['stations'][0]['arrival_time'])
        del order_data['selectedTrains']['trains'][0]['scale_pricing']
        del order_data['selectedTrains']['trains'][0]['stations']
        del order_data['selectedTrains']['trains'][0]['calendar']
        order_data['order_name']='test'            
        order_data['departure_hour']=departure_hour
        request.env['ticketing.order'].sudo().create({
                                        'name'                 :order_data['order_name'],
                                        'departure_date'       : order_data['departeurDate'],   
                                        'train1'               : order_data['selectedTrains']['trains'][0]['code'],
                                        'train2'               : order_data['selectedTrains']['trains'][1]['code'] if order_data['selectedTrains']['type']!='direct' else '', 
                                        'departure_hour'       : departure_hour ,
                                        'start_station'        : order_data['startStationSelected']['name'],
                                        'end_station'          : order_data['endStationSelected']['name'],
                                        'class_train'          : order_data['trainClassSelected']['name'],
                                        'correspondence'       : order_data['selectedTrains']['trains'][0]['correspondence']['name'],
                                        'distance'             : order_data['distance'],
                                        'traveler_profile'     : order_data['profileSelected']['name'],
                                        'passengers_number'    : order_data['travlerCount'],
                                        'passengers_discount'  : order_data['profileSelected']['discount'],
                                        'traveler_profile_with': order_data['profileWithSelected']['name'] if order_data['profileWithSelected'] else '',
                                        'companion_number'     : order_data['travlerWithCount'] if order_data['travlerWithCount'] else 0,
                                        'companion_discount'   : order_data['profileWithSelected']['discount'] if order_data['profileWithSelected'] else 0,
                                        'amount_total'         : order_data['price']['fullPrice'],
                                        'json_order'           : order_data,
                                        'order_type'           : 'sale',
                                        })

        return {"status": "ok"}
    

    def get_float_hour_from_string(self, time_str):
        return sum(int(x) * [1, 1/60][i] for i, x in enumerate(time_str.split(':')))
    


        
    @http.route('/get/pdf/order', type='json', auth='user')
    def get_pdf_order(self, **data):
        order_data = data
        ticket_width = 80 * mm
        ticket_height = 150 * mm
        # Création du buffer PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(ticket_width, ticket_height))
        top_margin = 2*mm
        y = ticket_height - top_margin

        left_x = 5*mm
        company = request.env.user.company_id
        if company.logo:
            logo_data = base64.b64decode(company.logo)
            logo_image = Image.open(BytesIO(logo_data))
            logo_width = 15 * mm 
            logo_height = 15 * mm
            c.drawInlineImage(logo_image, x=5*mm, y=y - logo_height - 5*mm, width=logo_width, height=logo_height)

        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_x + 20*mm, y - 5*mm, company.name)

        # --- QR code à droite ---
        qr_info = f"{order_data['startStationSelected']['name']} -> {order_data['endStationSelected']['name']} | Date: {order_data['departeurDate']} | Train: {order_data['selectedTrains']['trains'][0]['name']}"
        qr = qrcode.QRCode(box_size=2, border=1)
        qr.add_data(qr_info)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        img.save(qr_buffer)
        qr_buffer.seek(0)
        qr_image = ImageReader(qr_buffer)

        qr_width = 20*mm
        qr_height = 20*mm
        right_x = ticket_width - qr_width - 5*mm
        c.drawImage(qr_image, right_x, y - qr_height, width=qr_width, height=qr_height)

        y -= 30*mm  # descendre après logo/QR

        c.setFont("Helvetica", 8)

        # --- Ligne Départ → Arrivée ---
        c.drawString(left_x, y, f"Départ: {order_data['startStationSelected']['name']}")
        c.drawRightString(ticket_width - 5*mm, y, f"Arrivée: {order_data['endStationSelected']['name']}")
        y -= 5*mm

        # --- Ligne Date → Heure ---
        c.drawString(left_x, y, f"Date: {order_data['departeurDate']}")
        c.drawRightString(ticket_width - 5*mm, y, f"Heure: {order_data['departeurTime']}")
        y -= 5*mm

        # --- Ligne Distance → Prix ---
        c.drawString(left_x, y, f"Distance: {order_data['distance']} km")
        c.drawRightString(ticket_width - 5*mm, y, f"Prix: {order_data['price']['travler_price']} DA")
        y -= 5*mm

        # --- Classe et train ---
        c.drawString(left_x, y, f"Train: {order_data['selectedTrains']['trains'][0]['name']}")
        c.drawRightString(ticket_width - 5*mm, y, f"Classe: {order_data['trainClassSelected']['name']}")
        y -= 10*mm

        # --- Mentions légales ---
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(left_x, y, "Valable uniquement pour le train, la date et la classe indiqués.")
        y -= 4*mm  # descendre pour la ligne suivante
        c.drawString(left_x, y, "Conserver ce ticket c'est votre contrat d'assurance")

        
        c.showPage()
        c.save()
        buffer.seek(0)

        pdf_base64 = base64.b64encode(buffer.read()).decode('utf-8')
   
        return {"pdf": pdf_base64}