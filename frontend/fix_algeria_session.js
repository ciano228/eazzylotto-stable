/**
 * Correctif pour l'accès aux sessions Algeria depuis katooling_main_system
 */

// Correctif pour l'erreur pg_work_6
async function fixAlgeriaSessionAccess() {
    console.log('🔧 Application du correctif Algeria...');
    
    try {
        // 1. Récupérer les vraies sessions Algeria depuis katooling
        const response = await fetch('http://localhost:8881/api/katooling/algeria');
        const result = await response.json();
        
        if (result.status === 'success' && result.algeria_sessions) {
            console.log(`✅ ${result.algeria_sessions.length} sessions Algeria trouvées`);
            
            // 2. Mettre à jour le sélecteur de sessions
            const sessionSelect = document.getElementById('sessionSelect');
            if (sessionSelect) {
                // Supprimer les options PostgreSQL invalides
                Array.from(sessionSelect.options).forEach(option => {
                    if (option.value.startsWith('pg_work_') || option.value.startsWith('pg_session_')) {
                        option.remove();
                    }
                });
                
                // Ajouter les vraies sessions Algeria
                result.algeria_sessions.forEach(session => {
                    const option = document.createElement('option');
                    option.value = session.access_key;
                    option.textContent = `${session.name} (${session.actual_draws} tirages - ${session.type})`;
                    sessionSelect.appendChild(option);
                });
                
                // Sélectionner automatiquement la première session Algeria
                if (result.algeria_sessions.length > 0) {
                    sessionSelect.value = result.algeria_sessions[0].access_key;
                    console.log(`🎯 Session sélectionnée: ${result.algeria_sessions[0].access_key}`);
                    
                    // Charger automatiquement la session
                    await loadKatoolingSession(result.algeria_sessions[0].access_key);
                }
            }
        } else {
            console.warn('⚠️ Aucune session Algeria trouvée');
            await fallbackToMemorySessions();
        }
        
    } catch (error) {
        console.error('❌ Erreur correctif Algeria:', error);
        await fallbackToMemorySessions();
    }
}

// Fallback vers les sessions mémoire
async function fallbackToMemorySessions() {
    console.log('🔄 Fallback vers sessions mémoire...');
    
    try {
        const response = await fetch('http://localhost:8881/api/sessions');
        const result = await response.json();
        
        if (result.status === 'success' && result.sessions) {
            const sessionSelect = document.getElementById('sessionSelect');
            if (sessionSelect) {
                sessionSelect.innerHTML = '<option value="">Sélectionner une session...</option>';
                
                result.sessions.forEach(session => {
                    const option = document.createElement('option');
                    option.value = session.name;
                    option.textContent = `${session.name} (${session.completed_draws}/${session.total_draws})`;
                    sessionSelect.appendChild(option);
                });
                
                // Sélectionner session_test_001 par défaut
                const testSession = result.sessions.find(s => s.name === 'session_test_001');
                if (testSession) {
                    sessionSelect.value = 'session_test_001';
                    console.log('✅ Session_test_001 sélectionnée comme fallback');
                }
            }
        }
    } catch (error) {
        console.error('❌ Erreur fallback:', error);
    }
}

// Charger une session katooling
async function loadKatoolingSession(sessionId) {
    console.log(`📊 Chargement session katooling: ${sessionId}`);
    
    try {
        const response = await fetch(`http://localhost:8881/api/katooling/sessions/${sessionId}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            currentSession = result.session;
            displayKatoolingSessionInfo(currentSession);
            
            // Charger les tirages
            if (result.draws && result.draws.length > 0) {
                displaySessionDrawHistory(result.draws);
            }
            
            console.log(`✅ Session ${sessionId} chargée: ${result.completed_draws}/${result.total_draws} tirages`);
            
            return true;
        } else {
            console.error(`❌ Erreur chargement session: ${result.error}`);
            return false;
        }
        
    } catch (error) {
        console.error('❌ Erreur requête session:', error);
        return false;
    }
}

// Afficher les informations de session katooling
function displayKatoolingSessionInfo(session) {
    const infoDiv = document.getElementById('sessionInfo');
    if (!infoDiv) return;
    
    let html = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
            <div><strong>Session:</strong> ${session.name}</div>
            <div><strong>Type:</strong> ${session.type}</div>
            <div><strong>Total tirages:</strong> ${session.total_draws || 0}</div>
            <div><strong>Complétés:</strong> ${session.completed_draws || 0}</div>
        </div>
    `;
    
    if (session.lottery_type) {
        html += `<div style="margin-top: 10px;"><strong>Type de loterie:</strong> ${session.lottery_type}</div>`;
    }
    
    if (session.description) {
        html += `<div style="margin-top: 10px;"><strong>Description:</strong> ${session.description}</div>`;
    }
    
    infoDiv.innerHTML = html;
    infoDiv.style.display = 'block';
}

// Remplacer la fonction loadSelectedSession originale
async function loadSelectedSession() {
    const sessionName = document.getElementById('sessionSelect').value;
    if (!sessionName) {
        alert('Veuillez sélectionner une session');
        return;
    }
    
    console.log(`🔄 Chargement session: ${sessionName}`);
    
    // Vérifier si c'est une session katooling
    if (sessionName.startsWith('work_') || sessionName.startsWith('unified_')) {
        const success = await loadKatoolingSession(sessionName);
        if (success) {
            return;
        }
    }
    
    // Fallback vers l'ancienne méthode pour les sessions mémoire
    try {
        const response = await fetch(`http://localhost:8881/api/sessions/${sessionName}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            currentSession = result.session;
            displaySessionInfo(currentSession);
            
            // Charger les données de la session pour l'analyse
            await loadSessionData(sessionName);
            
            console.log(`✅ Session ${sessionName} chargée`);
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        console.error('Erreur chargement session:', error);
        alert(`Erreur lors du chargement de la session: ${error.message}`);
    }
}

// Actualiser les sessions avec support katooling
async function refreshSessions() {
    document.getElementById('sessionSelect').innerHTML = '<option value="">Chargement...</option>';
    document.getElementById('loadSessionBtn').disabled = true;
    
    // Appliquer le correctif Algeria qui charge toutes les sessions
    await fixAlgeriaSessionAccess();
    
    document.getElementById('loadSessionBtn').disabled = false;
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation correctif Algeria...');
    
    // Appliquer le correctif après un court délai
    setTimeout(async () => {
        await fixAlgeriaSessionAccess();
    }, 1000);
});

// Exposer les fonctions globalement pour compatibilité
window.fixAlgeriaSessionAccess = fixAlgeriaSessionAccess;
window.loadKatoolingSession = loadKatoolingSession;
window.loadSelectedSession = loadSelectedSession;
window.refreshSessions = refreshSessions;