/**
 * Simulation Currency Formatter
 * Include this in EVERY simulation template via:
 *   <script src="{{ url_for('static', filename='js/simulation_formatter.js') }}"></script>
 * Set the currency symbol BEFORE including this script:
 *   <script>window.CURRENCY_SYMBOL = "{{ currency_symbol }}";</script>
 */

(function() {
    'use strict';

    // Default fallback
    const CS = window.CURRENCY_SYMBOL || '$';

    // ===== FORMATTERS =====
    window.fmtMoney = function(val) {
        if (val === undefined || val === null || isNaN(val)) return CS + '0';
        return CS + Math.abs(parseFloat(val)).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    };

    window.fmtMoneySigned = function(val) {
        if (val === undefined || val === null || isNaN(val)) return CS + '0';
        const num = parseFloat(val);
        const abs = Math.abs(num).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
        if (num > 0) return '+' + CS + abs;
        if (num < 0) return '-' + CS + abs;
        return CS + '0';
    };

    window.fmtNum = function(val, decimals) {
        if (val === undefined || val === null || isNaN(val)) return 'N/A';
        return parseFloat(val).toFixed(decimals || 0);
    };

    window.fmtPercent = function(val, decimals) {
        if (val === undefined || val === null || isNaN(val)) return 'N/A';
        return parseFloat(val).toFixed(decimals || 1) + '%';
    };

    // ===== SIMULATION RESULT PARSER =====
    window.getSimValue = function(sim, key) {
        if (sim[key] !== undefined && sim[key] !== null) return sim[key];
        if (sim.results) {
            try {
                const r = JSON.parse(sim.results);
                if (r[key] !== undefined && r[key] !== null) return r[key];
            } catch(e) {
                try {
                    let fixed = sim.results
                        .replace(/True/g, 'true')
                        .replace(/False/g, 'false')
                        .replace(/None/g, 'null')
                        .replace(/'/g, '"');
                    const r = JSON.parse(fixed);
                    if (r[key] !== undefined && r[key] !== null) return r[key];
                } catch(e2) {}
            }
        }
        return undefined;
    };

    // ===== RISK BADGE CLASS =====
    window.riskBadgeClass = function(score) {
        const s = parseFloat(score) || 0;
        if (s >= 70) return 'badge-danger';
        if (s >= 40) return 'badge-warning';
        return 'badge-success';
    };

    // ===== COLOR CLASS FOR NUMBERS =====
    window.posNegClass = function(val, invert) {
        const num = parseFloat(val) || 0;
        if (invert) {
            return num < 0 ? 'text-success' : num > 0 ? 'text-danger' : 'text-muted';
        }
        return num >= 0 ? 'text-success' : 'text-danger';
    };

    // ===== ESCAPE HTML =====
    window.escapeHtml = function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    // ===== SAVE SIMULATION HELPER =====
    window.saveSimulation = async function(simId) {
        try {
            const response = await fetch(`/simulation/save/${simId}`, { method: 'POST' });
            const data = await response.json();
            if (data.success) alert('Simulation saved successfully!');
        } catch (error) {
            console.error('Error saving:', error);
        }
    };
})();