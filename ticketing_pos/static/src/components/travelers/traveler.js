/** @odoo-module **/

const { Component, useState, onWillStart,useEffect  } = owl;

export class Traveler extends Component {

    setup() {
        this.state = useState({
            filteredProfiles: [],
            profileSelected: [],
            profileWith: [],
            profileWithSelected: [],
            travlerCount:1,
            travlerWithCount:0,

        });

             // Réagit au chargement/changement de props.travelerProfile
        useEffect(
            () => {
             
              const travelerProfile = this.props.travelerProfile || [];

                if (travelerProfile.length === 0) {
                    return;
                }
                const defaultCategory = "ordinary";
                const defaultProfiles = travelerProfile.filter(p => p.category === defaultCategory);
                this.state.filteredProfiles = defaultProfiles;
                if (defaultProfiles.length > 0) {
                    const first = defaultProfiles[0];
                    this.state.profileSelected = first;
                    this.state.profileWith = first.profile_with || [];
                    // this.state.profileWithSelected =first.profile_with[0] || [];
                
                    this.props.onTravelerProfileChange(this.state.profileSelected)
                    // this.props.onTravelerProfileWithChange(this.state.profileWithSelected)
               

                }
            },
            () => [this.props.travelerProfile] 
          );

    }
    

    onTariffCategoryChange(ev) {
        const selectedCategory = ev.target.value;
        const filteredProfiles = this.props.travelerProfile.filter(
            profile => profile.category === selectedCategory
        );
        this.state.filteredProfiles = filteredProfiles;
        if (filteredProfiles.length > 0) {
            const firstProfile = filteredProfiles[0];
            this.state.profileSelected = firstProfile;
            // this.state.profileWith = firstProfile.profile_with || [];
            this.props.onTravelerProfileChange( this.state.profileSelected )
            // this.props.onTravelerProfileWithChange(this.state.profileWith)
            this.props.onTravelerCountChange(1)
            this.props.onTravelerWithCountChange(0)


        } else {
            this.state.profileSelected = [];
            this.state.profileWith = [];
            this.props.onTravelerProfileChange([])
            this.props.onTravelerProfileWithChange([])
            this.props.onTravelerCountChange(1)
            this.props.onTravelerWithCountChange(0)

        }
    }

    onTravelerProfileChange(ev) {
        const selectedId = parseInt(ev.target.value);
        console.log("onTravelerProfileChange",ev.target.value)

        if (!selectedId) return;
        const selectedProfile = this.props.travelerProfile.find(
            p => p.id === selectedId
        );
        if (selectedProfile) {
            this.state.profileSelected = selectedProfile;
            this.state.profileWith = selectedProfile.profile_with || [];
            this.props.onTravelerProfileChange(selectedProfile)

           
        }
    }
  
    onTravelerProfileWithChange(ev) {
        console.log("onTravelerProfileWithChange",ev.target.value)
        const selectedId = parseInt(ev.target.value);
        if (!selectedId) return;
        const selectedProfileWith = this.props.travelerProfile.find(
            p => p.id === selectedId
        );
        if (selectedProfileWith) {
            this.state.profileWithSelected = selectedProfileWith;
            this.props.onTravelerProfileWithChange(selectedProfileWith)
        }
    }

    onTravelerCountChange(ev){
      this.state.travlerCount = ev.target.value
           this.props.onTravelerCountChange(ev.target.value)
                    

    }
    onTravelerWithCountChange(ev){
        this.state.travlerWithCount = ev.target.value
        this.props.onTravelerWithCountChange(ev.target.value)
    }


}


Traveler.template = "Traveler";
