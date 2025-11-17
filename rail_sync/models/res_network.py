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


import hmac
import hashlib


class ResNetwork(models.Model):
    _inherit = 'res.network'


    config_file_ids = fields.One2many('config.file','network_id', string="Fichier de configuration")
    order_file_ids  = fields.One2many('order.file','network_id', string="Fichier des ventes")
    users_file_ids  = fields.One2many('users.file','network_id', string="Fichier des utilisateurs")



    def create_station(self,response):
        for s in response:
            self.env['res.station'].create({
                                "name"       : s['StationName_FR'],    
                                "code"       : s['NodeCode'],         
                                "name_arabe" : s['StationName_AR'],
                                "node_id"    : s['NodeId'],
                                                }) 


    def create_branch(self,code,name,distance):
        branch = self.env['res.branch'].search([('code','=',code)])
        if branch:
            return branch
        else : return self.env['res.branch'].create({
                                "name":name,
                                "amount_distance":distance,
                                "code":code,
                                })
    
    def create_branch_line(self,branch_id,node_id,distance,sequence):
        
        station_id = self.env['res.station'].search([('node_id','=',node_id)],limit=1)
        self.env['branch.station.line'].create({
                                                "station_id" :  station_id.id,
                                                "distance"   :  distance,   
                                                "branch_id"  :  branch_id.id  ,
                                                "sequence"   :  sequence,
                                        })
    
    def create_relation(self,code,name):
        return self.env['res.relation'].create({"name":name,"code":code})
    
    def create_train(self,ride):
        return self.env['res.train'].create({"name":ride.get("RIDENAME"),
                                             "code":ride.get("RIDECODE"),
                                             "date_from":ride.get("RIDESTARTDATE"),
                                             "date_to":ride.get("RIDEENDDATE"),
                                             "departure_time":self.datetime_to_float(ride.get('DEPARTURETIME')),
                                             "arrival_time": self.datetime_to_float(ride.get('ARRIVALTIME')),
                                             'start_station_id':self.env['res.station'].search([('node_id','=',ride.get("DEPNODEID"))],limit=1).id,
                                             'end_station_id':self.env['res.station'].search([('node_id','=',ride.get("ARRNODEID"))],limit=1).id,
                                             'branch_groupid':ride.get("BRANCHGROUPID")
                                             })

    def get_stop_station_with_distance(self,train,conn):
        relation = train.relation_id
        if not relation:
            return
        G = nx.Graph()
        # --- Construire le graphe à partir des branches ---
        for rel_branch in relation.branch_ids.sorted(key=lambda b: b.sequence):
            branch = rel_branch.branch_id
            lines = self.env['branch.station.line'].search(
                [('branch_id', '=', branch.id)], order='sequence'
            )
            previous_station = None
            for line in lines:
                station = line.station_id
                if previous_station:
                    # L’arête est pondérée par la distance relative
                    G.add_edge(previous_station.name, station.name, weight=line.distance)
                previous_station = station

        # --- Déterminer les stations de début et de fin ---
        start = train.start_station_id.name
        end = train.end_station_id.name

        if start not in G.nodes or end not in G.nodes:
            _logger.warning("Impossible de trouver %s -> %s dans le graphe pour le train %s", start, end,train.name)
            return

        # --- Trouver le plus court chemin ---
        try:
            path = nx.shortest_path(G, source=start, target=end, weight='weight')
        except nx.NetworkXNoPath:
            _logger.warning("Pas de chemin entre %s et %s", start, end)
            return

        # --- Calculer la distance cumulée ---
        total_dist = 0
        station_list = []
        for i, station_name in enumerate(path):
            if i > 0:
                prev_station = path[i - 1]
                total_dist += G[prev_station][station_name]['weight']
            station_list.append({
                'station': station_name,
                'distance_total': round(total_dist, 3)
            })

        # ---  Créer les lignes du train ---
        Station = self.env['res.station']
        Line = self.env['train.station.line']
        for s in station_list:
            station = Station.search([('name', '=', s['station'])], limit=1)
            # To Get departeur and arrival times of node 
            cur_rides = conn.cursor()
            cur_rides.execute(f"SELECT RIDEID FROM SNTFPEDITOWN.RIDES WHERE RIDECODE='{train.code}'")
            ride_id  = cur_rides.fetchone()[0]
            cur_rides.close()
            cur_ride_nodes = conn.cursor()
            cur_ride_nodes.execute(f"SELECT * FROM SNTFPEDITOWN.RIDE_NODE WHERE RIDEID='{ride_id}' AND NODEID='{station.node_id}'")
            row_ride_nodes = cur_ride_nodes.fetchone()
            if row_ride_nodes and station and station.node_id == row_ride_nodes[3] :
                Line.create({
                    'train_id': train.id,
                    'station_id': station.id,
                    'distance': s['distance_total'],
                    'sequence': station_list.index(s) + 1,
                    'arrival_time':self.datetime_to_float(row_ride_nodes[6]),
                })
            cur_ride_nodes.close()
        return station_list

    def get_data_from_oracle(self): 
        client = Client(wsdl='file:///home/reservationManager.wsdl')
        response = client.service.StationList(MaxItems=10000)
        # self.create_station(response)
        conn = cx_Oracle.connect(
                user="sys", password="sntfdb",
                dsn=cx_Oracle.makedsn('10.26.0.70', 1531, service_name='SNTFNDB'),
                mode=cx_Oracle.SYSDBA
            )
        schema, seen_bg, seen_b = "SNTFPEDITOWN", set(), set()

        # --- Récupération de toutes les RIDES ---
        cur_rides = conn.cursor()
        today = datetime.today().strftime("%Y-%m-%d")
        cur_rides.execute(f"SELECT * FROM {schema}.RIDES WHERE RIDETYPEID IN (1,2,3,11) AND RIDEENDDATE >= TO_DATE('{today}', 'YYYY-MM-DD')")
        cols_rides = [c[0] for c in cur_rides.description]
        for ride in map(lambda r: dict(zip(cols_rides, r)), cur_rides):
            train_obg = self.create_train(ride)
            bg_id = ride.get("BRANCHGROUPID")
            if not bg_id or bg_id in seen_bg: 
                continue
            seen_bg.add(bg_id)
            # --- BRANCHGROUPS ---
            cur_bg = conn.cursor()
            cur_bg.execute(f"SELECT * FROM {schema}.BRANCHGROUPS WHERE BRANCHGROUPID=:id", id=bg_id)
            for bg in map(lambda r: dict(zip([c[0] for c in cur_bg.description], r)), cur_bg):
                relation = self.create_relation(bg.get("BRANCHGROUPID"),bg.get("BRANCHGROUPNAME"))
                

                # --- BRANCHGROUP_BRANCH ---
                cur_bgb = conn.cursor()
                cur_bgb.execute(f"SELECT * FROM {schema}.BRANCHGROUP_BRANCH WHERE BRANCHGROUPID=:id ORDER BY ORDERNUM", id=bg_id)
                for bgb in map(lambda r: dict(zip([c[0] for c in cur_bgb.description], r)), cur_bgb):
                    branch_id = bgb.get("BRANCHID")
                    if branch_id not in seen_b: 
                        seen_b.add(branch_id)
                    # --- BRANCHES ---
                    cur_b = conn.cursor()
                    cur_b.execute(f"SELECT * FROM {schema}.BRANCHES WHERE BRANCHID=:id", id=branch_id)
                    for b in map(lambda r: dict(zip([c[0] for c in cur_b.description], r)), cur_b):
                        branch = self.create_branch(b.get("BRANCHID"),b.get("BRANCHNAME"), b.get("DISTANCEKM"))
                        relation.branch_ids = [(0, 0, {
                            "branch_id": branch.id,
                            "relation_id": relation.id,
                            "sequence": bgb.get("ORDERNUM"),
                        })]
                    cur_b.close()
                cur_bgb.close()
            cur_bg.close()
            
        # --- BRANCH_NODE ---
        cur_bn = conn.cursor()
        for i in seen_b:
            cur_bn.execute(f"SELECT * FROM {schema}.BRANCH_NODE WHERE BRANCHID = :id ORDER BY ORDERNUM", id=i)
            for bn in map(lambda r: dict(zip([c[0] for c in cur_bn.description], r)), cur_bn):
                branch_id = self.env['res.branch'].search([('code','=',bn.get("BRANCHID"))])
                self.create_branch_line(
                    branch_id,
                    bn.get("NODEID"),
                    bn.get("DISTANCEKM"),
                    bn.get("ORDERNUM")
                )

        #--- TRAIN TO RELATION ---

        for train in self.env['res.train'].search([]):
            train.relation_id = self.env['res.relation'].search([('code','=',train.branch_groupid)],limit=1).id
            self.get_stop_station_with_distance(train,conn)

        cur_bn.close()
        
     
        cur_rides.close()
        conn.close()

        _logger.warning("\n ok ok seen_bg=>%s",seen_bg)
        _logger.warning("\n ok ok seen_b=>%s",seen_b)

    def test_api(self,):
        client = Client(wsdl='file:///home/reservationManager.wsdl')
        response = client.service.RideSearch(
            DepartureNodeId = '2002',  
            ArrivalNodeId = '3001',
            DepartureDateTime='2025-10-13T12:00:00',  # UTC-4
            LanguageId='1',
            )
        

        for trip in response['RideTrips']['RideTrip']:
            for leg in trip['RideLegs']['RideLeg']:
                _logger.warning(f"\n Train {leg['RideCode']} le {leg['RideDate']} à {leg['DepartureTime']}")
       
      

        # response = client.service.RidePathTimeTable(
        #     RideDate='2025-10-14',
        #     RideOperatorId='5', 
        #     RideId='28',
        #     LanguageId='1',

        #     )
        # _logger.warning("\n response=>%s",response)
      


        # for service in client.wsdl.services.values():
        #     for port in service.ports.values():
        #         operations = port.binding._operations
        #         _logger.warning(f"\nService: {service.name}, Port: {port.name}")
        #         for operation in operations.values():
        #              _logger.warning(f"  - Operation: {operation.name}")


        # service = client.wsdl.services['reservationManager']
        # port = service.ports['reservationManagerPort']
        # operations = port.binding._operations

        # for op_name, operation in operations.items():
        #     _logger.warning(f"\nOperation: {op_name}")
        #     input_message = operation.input
        #     # Le message peut être DocumentMessage ou RpcMessage
        #     if hasattr(input_message, 'body'):
        #         # input_message.body est un Zeep Element
        #         elements = input_message.body.type.elements
        #         _logger.warning("Paramètres attendus:")
        #         for name, element in elements:
        #             _logger.warning(f" - {name}: {element.type}")
        #     else:
        #         _logger.warning("Pas de paramètres détectés")


    def create_json_file_data(self):
        data_dict = {'stations'        : self.get_station_data(),
                     'classes'         : self.get_classes(),
                     'trains'          : self.get_trains_with_trajectories(),
                     'traveler_profile': self.get_traveler_profile(),
                       }
        

        json_str = json.dumps(data_dict, separators=(",", ":"), ensure_ascii=False)
        encoded_file = base64.b64encode(json_str.encode('utf-8'))
        self.env['config.file'].create({
            'name': self.env['ir.sequence'].next_by_code('ir.sequence.config.file'),
            'file_data': encoded_file,
            'file_filename': 'config.json',
            'description': 'Fichier généré automatiquement',
            'is_active': True,
            'network_id': self.id
        })
        # self.build_train_graph()


    def get_station_data(self):
        stations = self.env['res.station'].search([],order='name')
        station_data = []
        for station in stations:
            station_data.append({
                'id': station.id,
                'name': station.name,
            })
        return station_data
    
    def get_classes(self):
        classes = self.env['res.class'].search([],order='name desc')
        class_data = []
        for clas in classes:
            class_data.append({
                'id': clas.id,
                'name': clas.name,
            })
        return class_data
    
    def get_traveler_profile(self):
        profiles_data = []
        profiles = self.env['traveler.profile'].search([],order='discount asc')
        for profile in profiles:
            profiles_data.append({
                'id': profile.id,
                'name': profile.name,
                'discount': profile.discount,
                'category': profile.category,
                'profile_with': [{'id':p.id,'name':p.name,'discount':p.discount} for p in profile.category_with_ids]
            })

        return profiles_data


    def get_trains_with_trajectories(self):
        trains = self.env['res.train'].search([], order='departure_time')
        train_data = []
        for i in range(1):
            for train in trains:
                stations = []
                for line in train.station_line_ids:
                    station_info = {
                        'id': line.station_id.id,
                        'name': line.station_id.name,
                        'arrival_time' : self.float_to_time_str(line.arrival_time),
                        'next_day': line.next_day,
                        'distance':line.distance,
                        
                    }
                    stations.append(station_info)
                scale_pricing=[]
                if train.scale_pricing_id:
                    scale_pricing.append({'id':train.scale_pricing_id.id,
                                          'name':train.scale_pricing_id.name,
                                           'minimum_perception':train.scale_pricing_id.minimum_perception,
                                           'calculation':[{ 'startkm':line.start_distance, 
                                                           'endkm':line.end_distance, 
                                                           'amount_untaxed':line.amount_untaxed,
                                                           'amount_stamp':line.amount_stamp,
                                                           'amount_total':line.amount_total,
                                                           'full_price':line.full_price,

                                                           } for line in train.scale_pricing_id.scale_calculation_ids]
                 
                                            })
                calendar={}  
                if train.calendar_id:
                   calendar = { 'id':train.calendar_id.id,
                                'name':train.calendar_id.name,
                                'monday' :train.calendar_id.monday,
                                'tuesday':train.calendar_id.tuesday,
                                'wednesday': train.calendar_id.wednesday,
                                'thursday':train.calendar_id.thursday,
                                'friday' :train.calendar_id.friday,
                                'saturday': train.calendar_id.saturday,
                                'sunday' :train.calendar_id.sunday,
                                'start_date' :train.calendar_id.start_date.strftime("%Y-%m-%d"),
                                'end_date' :train.calendar_id.end_date.strftime("%Y-%m-%d"),
                                'exception_dates' : [line.date.strftime("%Y-%m-%d") for line in train.calendar_id.exception_dates_ids]
                               }

                _logger.warning('\n ok ok calendar=>%s',calendar)

                train_data.append({
                    'id': train.id,
                    'name': train.name,
                    'code':train.code,
                    'stations': stations,
                    'scale_pricing' : scale_pricing,
                    'service':{'id':train.service_id.id,'name':train.service_id.name},
                    'calendar':calendar
                })

        
        return train_data

    def get_users_for_file(self):
        users = self.env['res.users.pos'].search([])
        data_dict = {'users': []}
        for u in users:
            data_dict['users'].append({
                "name": u.name,
                "login": u.login,
                "password": u.password,
                "code": u.code,
                "station_id": {
                    'id': u.station_id.id,
                    'name': u.station_id.name,
                    'node_id': u.station_id.node_id
                }
            })

        json_str = json.dumps(data_dict, separators=(",", ":"), ensure_ascii=False)
        secret_key = self.env['ir.config_parameter'].sudo().get_param('sync.secret.key', default='default_key')
        signature = hmac.new(secret_key.encode('utf-8'),msg=json_str.encode('utf-8'),digestmod=hashlib.sha256).hexdigest()
        signed_data = {'data': data_dict,'signature': signature}
        final_json_str = json.dumps(signed_data, separators=(",", ":"), ensure_ascii=False)
        encoded_file = base64.b64encode(final_json_str.encode('utf-8'))

        self.env['users.file'].create({
            'name': 'Users',
            'file_data': encoded_file,
            'file_filename': 'users.json',
            'description': 'Fichier généré automatiquement (signé)',
            'network_id': self.id
        })

    def verify_and_import_users(self, encoded_file):
        # Décoder
        file_content = base64.b64decode(encoded_file).decode('utf-8')
        signed_data = json.loads(file_content)

        data = signed_data.get('data')
        signature = signed_data.get('signature')

        secret_key = self.env['ir.config_parameter'].sudo().get_param('sync.secret.key', default='default_key')

        # Vérification HMAC
        recalculated_signature = hmac.new(
            secret_key.encode('utf-8'),
            msg=json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, recalculated_signature):
            pass
            # raise UserError("⚠️ Le fichier a été modifié ou est invalide !")

        # ✅ Si ok, continuer avec l'import
        for u in data.get('users', []):
            pass



    def create_orders(self):
        orderèfile_obj = self.env['order.file'].sudo().search([('synced','=',False)])
        for order_file in orderèfile_obj:
            decoded_json = base64.b64decode(order_file.file_data).decode('utf-8')
            json_data = json.loads(decoded_json)  
            for order_data in json_data['data'] :  
                _logger.warning('\n ok ok order =>%s', order_data)
                departure_hour = self.get_float_hour_from_string(order_data['departeurTime'])
                order_data['departure_hour']=departure_hour
                self.env['ticketing.order'].sudo().create({
                        'name'                      :"order_data['order_name']",
                        'departure_date'            : order_data['departeurDate'],          
                        'departure_hour'            : departure_hour ,
                        'start_station'             : order_data['startStationSelected']['name'],
                        'start_station_id'              : order_data['startStationSelected']['id'],
                        'end_station'               : order_data['endStationSelected']['name'],
                        'end_station_id'                : order_data['endStationSelected']['id'],

                        'class_train'               : order_data['trainClassSelected']['name'],
                        'class_train_id'                : order_data['trainClassSelected']['id'],
                        'correspondence'            : order_data['selectedTrains']['trains'][0]['correspondence']['name'],
                        'correspondence_id'             : order_data['selectedTrains']['trains'][0]['correspondence']['id'] if order_data['selectedTrains']['trains'][0]['correspondence']!=0 else False,
                        'distance'                  : order_data['distance'],
                        'traveler_profile'          : order_data['profileSelected']['name'],
                        'traveler_profile_id'           : order_data['profileSelected']['id'],
                        'passengers_number'         : order_data['travlerCount'],
                        'passengers_discount'       : order_data['profileSelected']['discount'],
                        'traveler_profile_with'     : order_data['profileWithSelected']['name'] if order_data['profileWithSelected'] else '',
                        'traveler_profile_with_id'      : order_data['profileWithSelected']['name'] if order_data['profileWithSelected'] else False,
                        'companion_number'          : order_data['travlerWithCount'] if order_data['travlerWithCount'] else 0,
                        'companion_discount'        : order_data['profileWithSelected']['discount'] if order_data['profileWithSelected'] else 0,
                        'amount_total'              : order_data['price']['fullPrice'],
                        'json_order'                :   json.dumps(order_data),
                                                
                                                })
        

    def float_to_time_str(self,value):
        if value is None:
            return None
        hours = int(value)
        minutes = int(round((value - hours) * 60))
        return f"{hours:02d}:{minutes:02d}"
    

    def datetime_to_float(self,dt):
        if dt is None:
            return 0.0
        if isinstance(dt, datetime):
            hour = dt.hour
            minute = dt.minute
        elif isinstance(dt, time):
            hour = dt.hour
            minute = dt.minute
        else:
            raise TypeError(f"Type non supporté : {type(dt)}")
        return hour + (minute / 60.0)
   
    def get_float_hour_from_string(self, time_str):
        return sum(int(x) * [1, 1/60][i] for i, x in enumerate(time_str.split(':')))