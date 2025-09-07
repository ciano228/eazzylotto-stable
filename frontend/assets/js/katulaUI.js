// Module d'interface utilisateur Katula
import { FORME_ICONS } from './katulaConstants.js';

export function showChipDetails(chipNumber, universeData) {
    const chipData = universeData.chipDetails[chipNumber];
    if (!chipData || !chipData.formes_data || Object.keys(chipData.formes_data).length === 0) {
        alert(`chip${chipNumber}: Aucune donnée disponible`);
        return;
    }
    
    const formesData = chipData.formes_data;
    let details = `🎯 chip${chipNumber} - ${universeData.universe.toUpperCase()}\n\n`;
    
    // Organiser par forme
    Object.entries(formesData).forEach(([forme, items]) => {
        const icon = FORME_ICONS[forme] || '?';
        details += `${icon} ${forme.toUpperCase()}:\n`;
        items.slice(0, 3).forEach(item => {
            details += `  • ${item.denomination}\n`;
        });
        if (items.length > 3) {
            details += `  ... et ${items.length - 3} autres\n`;
        }
        details += '\n';
    });
    
    const totalItems = Object.values(formesData).reduce((sum, items) => sum + items.length, 0);
    details += `📊 Total: ${totalItems} éléments`;
    alert(details);
}

export async function showDenominationDetails(denomination, universe, event, API_BASE) {
    event.stopPropagation();
    
    if (denomination === '---') return;
    
    try {
        const denominations = denomination.split('/').map(d => d.trim());
        let allCombinations = [];
        
        for (const singleDenomination of denominations) {
            const url = `${API_BASE}/denomination/${universe}/${encodeURIComponent(singleDenomination)}`;
            const response = await fetch(url);
            
            if (response.ok) {
                const data = await response.json();
                if (data.details && data.details.length > 0) {
                    allCombinations.push(...data.details);
                }
            }
        }
        
        if (allCombinations.length === 0) {
            alert(`Aucune combinaison trouvée pour "${denomination}" dans ${universe}`);
            return;
        }
        
        // Afficher les détails
        let details = `🎯 ${denomination.toUpperCase()} - ${universe.toUpperCase()}\n\n`;
        details += `📊 Total: ${allCombinations.length} combinaisons\n\n`;
        
        allCombinations.slice(0, 10).forEach((combo, i) => {
            details += `${i+1}. ${combo.num1}-${combo.num2} (${combo.alpha_ranking || 'N/A'})\n`;
        });
        
        if (allCombinations.length > 10) {
            details += `\n... et ${allCombinations.length - 10} autres`;
        }
        
        alert(details);
        
    } catch (error) {
        showError('Erreur: ' + error.message);
    }
}

export function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    document.querySelector('.container').appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

export function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    document.querySelector('.container').appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}