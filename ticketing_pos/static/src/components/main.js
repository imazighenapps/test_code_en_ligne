/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { Stations } from "./stations/station"
import { Trains } from "./trains/train"
import { Tarifs } from "./tarifs/tarif"
import { Traveler } from "./travelers/traveler"
import { Shortcuts } from "./shortcuts/shortcuts"
import { PrintStatus } from "./status/print_status"
import { loadJS } from "@web/core/assets";

const { Component, onWillStart, onMounted, useRef, useState } = owl;

export class TicketingPos extends Component {

    setup() {
        this.state = useState({ stations:[],
                                classes:[],
                                travelerProfile:[],
                                allTrains:[],
                                availableTrains:[],
                                filtredTrainsByDateTime:[],
                                startStationSelected: null,
                                endStationSelected: null,
                                trainClassSelected: null,
                                selectedTrains : null,
                                profileSelected: [],
                                profileWithSelected: [],
                                travlerCount: 1,
                                travlerWithCount:0,
                                departeurDate:'',
                                departeurTime:'',
                                distance : 0,
                                price:{},
                                shortcuts:[],
                                printerName:'EPSON TM-T88V Receipt',
                                
                                });

        onWillStart(async () => {
            const JSfile = "/ticketing_pos/static/src/lib/jspdf.js";
            await loadJS(JSfile);          
        });

        onMounted(() => {
            this.loadData();
            let self=this    
            const handleKeyDown = (event) => {
                 // Vérifie si SHIFT est pressé + une seule lettre
                if (event.shiftKey && /^[a-z0-9]$/i.test(event.key)) {
                    const pressedKey = event.key.toLowerCase();
                    const shortcutItem = this.state.shortcuts.find((s) => s.shortcut.toLowerCase() === pressedKey);
                    if (shortcutItem) {
                        self.onEndStationSelected(shortcutItem.station_id)
                    }
                }else if (event.key === "Enter"){
                   console.log('enter')
                   self.validateOrder()
                } 
            };

            window.addEventListener("keydown", handleKeyDown);
            this._removeKeyDownListener = () => {
                window.removeEventListener("keydown", handleKeyDown);
            };
        });

    }

    async loadData(){
        let self=this
        await rpc("/lead/data",{
        }).then(function(result){
            self.state.stations = result.stations
            self.state.classes = result.classes
            self.state.allTrains = result.trains
            self.state.travelerProfile = result.traveler_profile
            self.state.trainClassSelected = result.classes[0]['id']
        })   

    }

    getShortcuts = (value) => {
        this.state.shortcuts = value;
        
    }
    onStartStationSelected = (value) => {
        this.state.startStationSelected = value;
        this.loadAvailableTrains()
    }

    onEndStationSelected = (value) => {
        this.state.endStationSelected = value;
        this.loadAvailableTrains()

    }

    onTrainClassSelected = (value) => {
    
        this.state.trainClassSelected = value;
        this.loadAvailableTrains()
    }
    
    async loadAvailableTrains() {
            const startTime = performance.now(); 
            const self = this;
            const directTrains = [];
            const connectingTrains = [];
            const firstTrains = [];
            const lastTrains = [];
            if (self.state.startStationSelected !== null && self.state.endStationSelected !== null && self.state.trainClassSelected !== null) {
                const startId = parseInt(self.state.startStationSelected);
                const endId = parseInt(self.state.endStationSelected);
                // === Étape 1 : Rechercher les trains directs ===
                for (const train of self.state.allTrains) {
                    const stationIds = train.stations.map((st) => st.id);
                    const startIndex = stationIds.indexOf(startId);
                    const endIndex = stationIds.indexOf(endId);
                    if (startIndex !== -1 && endIndex !== -1 && startIndex < endIndex) {
                        const filteredStations = train.stations.slice(startIndex, endIndex + 1);
                        const filteredTrain = {
                            ...train,
                            stations : filteredStations,
                            duration :self.getDurationHHMM(filteredStations[0].arrival_time, filteredStations[filteredStations.length - 1].arrival_time),
                            terminus : train.stations[train.stations.length - 1],
                            distance : self.get_distance({type: "special", station:filteredStations}),
                            correspondence: {'id':0,name:"/"},
                        };
                        directTrains.push({ type: "direct", trains: [filteredTrain] });
                    }
                    // === prepare les trains pour la correspondence ===
                     if (startIndex !== -1 && endIndex === -1) {
                        firstTrains.push({ type: "first", trains: [train] });
                    }
                    if (endIndex !== -1 && startIndex === -1) {
                        lastTrains.push({ type: "second", trains: [train] });
                    }
                }
    
                // === Étape 2 : Rechercher les trains avec correspondance ===
                let i=0
                for (const firstItem of firstTrains) {
                    const trainA = firstItem.trains[0];
                    const stationsA = trainA.stations.map((st) => st.id);
                    for (const lastItem of lastTrains) {
                        i++
                        const trainB = lastItem.trains[0];
                        if (trainA.name === trainB.name) {continue;}
                        const stationsB = trainB.stations.map((st) => st.id);
                        const intersection = stationsA.filter((id) => stationsB.includes(id));
                        if (intersection.length > 0) {
                            const correspondence =   intersection[0] 
                            const startIndex = stationsA.indexOf(startId);
                            const endIndex = stationsB.indexOf(endId);
                            const correspondenceIndexA =  stationsA.indexOf(correspondence);  
                            const correspondenceIndexB =  stationsB.indexOf(correspondence); 
    
                            if (startIndex !== -1 && correspondenceIndexA !== -1 && startIndex < correspondenceIndexA && endIndex!==-1 && correspondenceIndexB < endIndex) {
                                const filteredStationsA = trainA.stations.slice(startIndex, correspondenceIndexA + 1);
                                const filteredTrainA = {
                                    ...trainA,
                                    stations: filteredStationsA,
                                    terminus : trainA.stations[trainA.stations.length - 1],
                                    distance : self.get_distance({type: "special", station:filteredStationsA}),
                                    duration :self.getDurationHHMM(filteredStationsA[0].arrival_time, filteredStationsA[filteredStationsA.length - 1].arrival_time),
                                    correspondence : filteredStationsA[filteredStationsA.length - 1]
                                };
    
                                // Filtrer les stations de trainB : de correspondence → end
                                const filteredStationsB = trainB.stations.slice(correspondenceIndexB, endIndex + 1);
                                const filteredTrainB = {
                                    ...trainB,
                                    stations: filteredStationsB,
                                    terminus : trainB.stations[trainB.stations.length - 1],
                                    distance : self.get_distance({type: "special", station:filteredStationsB}),
                                    duration :self.getDurationHHMM(filteredStationsB[0].arrival_time, filteredStationsB[filteredStationsB.length - 1].arrival_time),
                                    correspondence : filteredStationsB[0]
                                };
                                const arrivalA = filteredStationsA[filteredStationsA.length - 1].arrival_time;
                                const departureB = filteredStationsB[0].arrival_time;   
                                const arrivalMinutesA = self.timeToMinutes(arrivalA);
                                const departureMinutesB = self.timeToMinutes(departureB);  
                                if (arrivalMinutesA < departureMinutesB) {
                                    connectingTrains.push({ type: "connecting", trains: [filteredTrainA, filteredTrainB]});
                                     break;
                                }    
                              
                            }
                        }
                    }
                }
    
            self.state.availableTrains = directTrains.concat(connectingTrains);

            const endTime = performance.now();
            const durationSeconds = ((endTime - startTime) / 1000).toFixed(3); 
            console.log(`loadAvailableTrains duration: ${durationSeconds} seconds`);
            // self.onTrainsSelected(self.state.availableTrains[0])
            self.filterTrainByDateTime()
    
        }
       
        }
    
    filterTrainByDateTime() {
        const self = this;
        function timeToMinutes(timeStr) {
            if (!timeStr) return 0;
                const [h, m] = timeStr.split(':').map(Number);
                return h * 60 + m;
            }
            // 🔹 Récupérer l’heure de départ du premier train
            function getFirstDeparture(trainObj) {
                const firstTrain = trainObj.trains[0];
                const firstStation = firstTrain.stations[0];
                return timeToMinutes(firstStation.departure_time || firstStation.arrival_time);
            }
        // 🔹 Tri par heure de départ
        self.state.availableTrains.sort((a, b) => {
                return getFirstDeparture(a) - getFirstDeparture(b);
            });

        self.state.filtredTrainsByDateTime = [];
        if (self.state.availableTrains.length > 0) {
            const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
            const date = new Date(self.state.departeurDate);
            const dayName = days[date.getDay()];
            const departeurTime = self.state.departeurTime;
            const availableTrains = JSON.parse(JSON.stringify(self.state.availableTrains));
            const filteredTrains = [];
            for (const item of availableTrains) {
                item.selected = false;
                item.display = false;
                const isDirect = item.type === "direct";
                const train0 = item.trains[0];
                const train1 = item.trains[1];
                const stations0 = train0.stations;
                const stations1 = train1?.stations;
                const calendar0 = train0.calendar || {};
                const calendar1 = train1?.calendar || {};

                const hasServiceToday0 = calendar0[dayName];
                const hasServiceToday1 = isDirect ? true : calendar1[dayName];

                const exceptions0 = calendar0['exception_dates'] || [];
                const exceptions1 = isDirect ? [] : (calendar1['exception_dates'] || []);

                const isExceptionDate0 = exceptions0.includes(self.state.departeurDate);
                const isExceptionDate1 = isDirect ? false : exceptions1.includes(self.state.departeurDate);

                // Condition d'acceptation des trains
                if (isDirect) {
                    if (stations0[0].arrival_time > departeurTime && hasServiceToday0 && !isExceptionDate0) {
                        item.display = true;
                    }
                } else {
                    const arriveTooEarly = stations0[0].arrival_time <= departeurTime;
                    const timeToMinutes = (timeStr) => {
                            const [hours, minutes] = timeStr.split(':').map(Number);
                            return hours * 60 + minutes;
                                    };
                    const arrival1 = timeToMinutes(stations1[0].arrival_time);
                    const arrival0 = timeToMinutes(stations0[stations0.length - 1].arrival_time);                    
                    const overlap = (stations1[0].arrival_time <= stations0[stations0.length - 1].arrival_time) || (arrival1 - arrival0) > 50;
                    if (!arriveTooEarly && !overlap && hasServiceToday0 && hasServiceToday1 && !isExceptionDate0 && !isExceptionDate1)
                        {
                            item.display = true;
                        }
                }
                if (item.display) {
                    filteredTrains.push(item);
                }
            }
            // Marquer le premier train sélectionné s'il y en a un
            if (filteredTrains.length > 0) {
                filteredTrains[0].selected = true;
            }

            self.state.filtredTrainsByDateTime = filteredTrains;
            self.state.distance = self.get_distance(filteredTrains[0])
            self.state.selectedTrains = filteredTrains[0]
            self.get_price()

        }    
    }




    get_distance(item){
        
        let distance = 0
        if(item){
            if(item.type==="special"){
                distance = item.station[item.station.length - 1].distance - item.station[0].distance  
            } 
            if(item.type==="direct"){
                distance = item.trains[0].stations[item.trains[0].stations.length - 1].distance - item.trains[0].stations[0].distance  
            } 
            if(item.type==="connecting"){
            let distA = item.trains[0].stations[item.trains[0].stations.length - 1].distance - item.trains[0].stations[0].distance  
            let distB = item.trains[1].stations[item.trains[1].stations.length - 1].distance - item.trains[1].stations[0].distance  
            distance = distA + distB
            } 
        }
        return Math.round(distance)
    }



    get_price(){
        let self=this;
     
        let price_line={}
        if(self.state.selectedTrains!==null && self.state.trainClassSelected!==null && self.state.distance!==0){
            for (const sp of self.state.selectedTrains.trains[0].scale_pricing ){
                for (const line of sp.calculation){
                    if (line.startkm <=  parseInt(self.state.distance) && line.endkm >= parseInt(self.state.distance)){
                         price_line={
                                amount_stamp:line.amount_stamp,
                                amount_total:line.amount_total,
                                amount_untaxed:line.amount_untaxed,
                                full_price:line.full_price,
                                minimum_perception:sp.minimum_perception,
                         }
                    }
                }
            }    
        }  

        let profilDiscount     = parseInt(self.state.profileSelected.discount)
        let travlerCount       = parseInt(self.state.travlerCount)
        let profilWithDiscount = parseInt(self.state.profileWithSelected.discount) || 0
        let travlerWithCount   = parseInt(self.state.travlerWithCount)
        

        let travler_price = self.calculateFullPrice(price_line.full_price, travlerCount, profilDiscount) 
        if (travler_price < price_line.minimum_perception && travlerCount>0){
                travler_price = price_line.minimum_perception
            }
    
        let travler_with_price =   self.calculateFullPrice(price_line.full_price, travlerWithCount, profilWithDiscount) 
        
        if (travler_with_price < price_line.minimum_perception && travlerWithCount>0){
                travler_with_price = price_line.minimum_perception
            }

        self.state.price={
            ht:self.calculateFullPrice(price_line.amount_untaxed, travlerCount, profilDiscount)+self.calculateFullPrice(price_line.amount_untaxed, travlerWithCount, profilWithDiscount),
            amount_total:self.calculateFullPrice(price_line.amount_total, travlerCount, profilDiscount) + self.calculateFullPrice(price_line.amount_total,travlerWithCount,profilWithDiscount),
            amount_stamp:7,
            travler_price:travler_price,
            travler_with_price:travler_with_price,
            fullPrice :travler_price+travler_with_price,
                            } 

        
                    
        
    }
    
    calculateFullPrice(basePrice, nb, discount) {
        const price = basePrice * nb * (1 - discount / 100);
        return price

    }


    onTrainsSelected = (selectedItem) => {
        if(selectedItem){
            let self=this
            for (const item of self.state.filtredTrainsByDateTime ) {
                if (item.trains[0].id===selectedItem.trains[0].id){
                    item.selected = true;
                }else{
                    item.selected = false;
                }

            }
            this.state.selectedTrains = selectedItem;
            let distance = this.get_distance(selectedItem)
            this.state.distance = distance;
            this.get_price()
        }
    }
    
     onTravelerProfileChange=(value)=>{
        this.state.profileSelected = value;
          this.get_price()
     }

    onTravelerProfileWithChange=(value)=>{
        this.state.profileWithSelected = value;
        this.get_price()
    }

    onTravelerCountChange=(value)=>{
        this.state.travlerCount = value;
          this.get_price()
    }
    onTravelerWithCountChange=(value)=>{
        this.state.travlerWithCount = value;
        this.get_price()
    }  


    getDeparteurDate=(departeurDate)=>{
        this.state.departeurDate = departeurDate
        this.filterTrainByDateTime()
    }

    getDeparteurTime=(departeurTime)=>{
        this.state.departeurTime = departeurTime
        this.filterTrainByDateTime()
    }

    
    getDurationHHMM(startTime, endTime) {
        const [startHour, startMinute] = startTime.split(":").map(Number);
        const [endHour, endMinute] = endTime.split(":").map(Number);
        const startTotal = startHour * 60 + startMinute;
        const endTotal = endHour * 60 + endMinute;
        let diff = endTotal - startTotal;
        if (diff < 0) {
            diff += 24 * 60;
        }
        const hours = Math.floor(diff / 60);
        const minutes = diff % 60;
        const paddedHours = String(hours).padStart(2, "0");
        const paddedMinutes = String(minutes).padStart(2, "0");
        return `${paddedHours}:${paddedMinutes}`;
    }  

    sumDurationsHHMM(duration1, duration2) {
        const [h1, m1] = duration1.split(":").map(Number);
        const [h2, m2] = duration2.split(":").map(Number);

        let totalMinutes = h1 * 60 + m1 + h2 * 60 + m2;

        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;

        const paddedHours = String(hours).padStart(2, "0");
        const paddedMinutes = String(minutes).padStart(2, "0");

        return `${paddedHours}:${paddedMinutes}`;
    }


    timeToMinutes(timeStr) {
        if (!timeStr) return 0;
        const [h, m] = timeStr.split(':').map(Number);
        return h * 60 + m;
    }

    validateOrder() {
        let self=this
        let order={}
        const params={
                startStationSelected: self.state.stations.find(s => parseInt(s.id) === parseInt(self.state.startStationSelected)),
                endStationSelected: self.state.stations.find(s => parseInt(s.id) === parseInt(self.state.endStationSelected)),
                trainClassSelected: self.state.classes.find(c => parseInt(c.id) === parseInt(self.state.trainClassSelected)),
                selectedTrains : self.state.selectedTrains,
                profileSelected: self.state.profileSelected,
                profileWithSelected: self.state.profileWithSelected,
                travlerCount: self.state.travlerCount,
                travlerWithCount:self.state.travlerWithCount,
                departeurDate:self.state.departeurDate,
                departeurTime:self.state.departeurTime,
                distance : self.state.distance,


                price:self.state.price,
        }

    
        rpc("/save/order", {params});
          self.printTicket(params) 
    }  
    async printTicket(orderData) {
        const self = this;

        try {
            const result = await rpc(
                    "/get/pdf/order",
                    orderData,
            );

            const pdfBase64 = result.pdf;
            const pdfBlob = new Blob([Uint8Array.from(atob(pdfBase64), c => c.charCodeAt(0))], { type: "application/pdf" });

            const formData = new FormData();
            formData.append("file", pdfBlob, "ticket.pdf");
            formData.append("printerName", "EPSON TM-T88V Receipt");

            const printResponse = await fetch("http://localhost:8081/print", {
                method: "POST",
                body: formData,
            });

            const text = await printResponse.text();
            alert("Ticket envoyé à l'impression : " + text);

        } catch (error) {
            console.error("Erreur lors de l'impression :", error);
            alert("Erreur lors de l'impression : " + error.message);
        }
    }


    async checkPrinterStatus(printerName) {
        try {
            const response = await fetch(`http://localhost:8081/printer/status?printerName=${encodeURIComponent(printerName)}`);
            const status = await response.text(); // retourne "true" ou "false"
            if (status === "true") {
                console.log(`Imprimante ${printerName} disponible`);
                return true;
            } else {
                console.log(`Imprimante ${printerName} non disponible`);
                return false;
            }
        } catch (error) {
            console.error("Erreur lors de la vérification de l'imprimante :", error);
            return false;
        }
    }

}


TicketingPos.components = {Stations,Trains,Tarifs,Traveler,Shortcuts,PrintStatus}

TicketingPos.template = "main";
registry.category("actions").add("ticketing_pos", TicketingPos);
