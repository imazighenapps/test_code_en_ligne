
/** @odoo-module */

const { Component, onWillUnmount,onWillUpdateProps, useRef,useState, onMounted } = owl


export class Tarifs extends Component {

  setup() {
        let self=this
        this.state = useState({ serverStatus:false,
                                });

        let intervalId = null;
        const updateDateTime = () => {
            const now = new Date();
            const today = now.toISOString().split("T")[0];
            const hours = String(now.getHours()).padStart(2, "0");
            const minutes = String(now.getMinutes()).padStart(2, "0");
            const timeString = `${hours}:${minutes}`;
            self.props.getDeparteurDate(today)
            self.props.getDeparteurTime(timeString)
        };

        onMounted(() => {
            updateDateTime();
            intervalId = setInterval(updateDateTime, 60000);
        });

        onWillUnmount(() => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        });
    }
       
 

 

    
    changeDeparteurDate(ev){
         this.props.getDeparteurDate?.(ev.target.value)

    }
    changeDeparteurTime(ev){
           console.log('ev.target.value=>',ev.target.value) 
         this.props.getDeparteurTime?.(ev.target.value)

    }

}

Tarifs.template = "Tarifs"