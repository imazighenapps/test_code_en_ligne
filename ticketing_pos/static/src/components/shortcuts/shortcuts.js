/** @odoo-module **/

import { Component, onMounted, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class Shortcuts extends Component {
    setup() {
        this.notification = useService("notification");

        this.state = useState({
            shortcuts: [],
        });

        onMounted(async () => {
            await this.loadShortcuts();
        });
    }

    async loadShortcuts() {
        try {
            const shortcuts = await rpc("/shortcut/load", []);
            this.state.shortcuts = shortcuts;
            this.props.getShortcuts(shortcuts)
        } catch (e) {
            console.error("Erreur de chargement :", e);
        }
    }

    addShortcut(ev) {
        ev.stopPropagation();
        // Générer un ID unique avec timestamp
        const newId = Date.now();
        this.state.shortcuts = [
            ...this.state.shortcuts,
            {
                id: newId,
                station_id: "",
                station_name: "",
                shortcut: "",
            },
        ];
    }

    removeShortcut(ev) {
        ev.stopPropagation();
        // Trouver le bouton cliqué
        let target = ev.target;
        while (target && target.tagName !== "BUTTON") {
            target = target.parentElement;
        }
        if (!target) return;

        const id = parseInt(target.id);
        // Supprimer le shortcut avec l'id correspondant
        this.state.shortcuts = this.state.shortcuts.filter(s => s.id !== id);
    }

    onStationChange(ev) {
        const selectedStationId = ev.target.value;
        const selectedStationName = this.props.stations.find(s => String(s.id) === selectedStationId)?.name || "";

        const shortcutId = parseInt(ev.target.id);
        const index = this.state.shortcuts.findIndex(s => s.id === shortcutId);

        if (index !== -1) {
            const newShortcuts = [...this.state.shortcuts];
            newShortcuts[index] = {
                ...newShortcuts[index],
                station_id: parseInt(selectedStationId),
                station_name: selectedStationName,
            };
            this.state.shortcuts = newShortcuts;
        }
    }

    onShortcutChange(ev) {
        const id = parseInt(ev.target.id);
        const index = this.state.shortcuts.findIndex(s => s.id === id);
        if (index !== -1) {
            const newShortcuts = [...this.state.shortcuts];
            newShortcuts[index] = {
                ...newShortcuts[index],
                shortcut: ev.target.value,
            };
            this.state.shortcuts = newShortcuts;
        }
    }

    async saveShortcuts(ev) {
        ev.stopPropagation();
        const shortcuts = this.state.shortcuts.filter(s => s.station_id && s.shortcut);
        let self=this
        self.props.getShortcuts(shortcuts)
        try {
            await rpc("/shortcut/save", { shortcuts });
            this.notification.add(
                "Raccourcis enregistrés avec succès.",
                {type: "success"},
            );
        } catch (e) {
            console.error("Erreur lors de l'enregistrement :", e);
            this.notification.add(
               "Erreur lors de l'enregistrement des raccourcis.",
                {type: "danger"}
            );
        }
    }
}
Shortcuts.template = "Shortcuts";
