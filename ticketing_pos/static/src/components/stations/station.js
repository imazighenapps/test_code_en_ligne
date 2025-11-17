
/** @odoo-module */

const { Component, onWillUnmount,onWillDestroy, useRef,useState, onMounted } = owl
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class Stations extends Component {

    setup(){
        
      this.state = useState({
            startStation: null,
            endStation: null,
            trainClass: null,
        });
    }
    
    onStartStationChange(ev) {
        const val = ev.target.value;
        if (!val) {
            return;
        }
        this.state.startStation = ev.target.value;
        this.props.onStartStationSelected?.(ev.target.value);
    }

    onEndStationChange(ev) {
        const val = ev.target.value;
         console.log('End Station', val)
        if (!val) {
            return;
        }
        this.state.endStation = ev.target.value;
        this.props.onEndStationSelected?.(ev.target.value);
    }

    onTrainClassChange(ev) {
        const val = ev.target.value;
        console.log('class', val)
        if (!val) {
            return;
        }
        this.state.trainClass = ev.target.value;
        this.props.onTrainClassSelected?.(ev.target.value);
    }

   
 


}

Stations.template = "Stations"