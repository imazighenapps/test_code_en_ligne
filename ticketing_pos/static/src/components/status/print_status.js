/** @odoo-module */

const { Component, onMounted, onWillUnmount, useState } = owl;
// const { ajax } = require('web.rpc'); // ou fetch natif si tu veux

export class PrintStatus extends Component {
    setup() {
        let self=this
        this.state = useState({
            ApiStatus: false, 
            printerStatus: false,
        });

        let intervalId = null;

        const updateStatus = async () => {
            try {const response = await fetch("http://localhost:8081/health", {method: "GET",});
                if (response.ok) {
                    this.state.ApiStatus = true;
                } else {
                    this.state.ApiStatus = false;
                }
            } catch (error) {
                this.state.ApiStatus = false;
            }
            
            try {const response = await fetch(`http://localhost:8081/printer/status?printerName=${encodeURIComponent(self.props.printerName)}`);
                const status = await response.text(); // retourne "true" ou "false"
                if (status === 'true') {
                     self.state.printerStatus= true;
                } else {
                     self.state.printerStatus = false;
                }
        } catch (error) {
            self.state.printerStatus = false;
        }



        };

        onMounted(() => {
            updateStatus(); // Vérifier immédiatement
            intervalId = setInterval(updateStatus, 3000); // Vérifier toutes les 3s
        });

        onWillUnmount(() => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        });
    }
}

PrintStatus.template = "PrintStatus";
