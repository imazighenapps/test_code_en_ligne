/** @odoo-module */

const { Component, useState, onWillStart, onWillUpdateProps } = owl;
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class Trains extends Component {
    setup(){
    
    }

    selectTrains(item){
        
        this.props.onTrainsSelected(item);
        
    }

   
}

Trains.template = "Trains"
