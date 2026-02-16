"""
Script pour réparer smart-input-v2.html en ajoutant la fonction loadSessions manquante
"""
import re

# Chemin du fichier
file_path = r"c:\Users\User\eazzycalculator\frontend\smart-input-v2.html"

# Lire le fichier
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# La fonction loadSessions à ajouter
load_sessions_function = """
        // Load sessions from API
        async function loadSessions() {
            try {
                const response = await fetch(`${API_BASE}/session/sessions`);
                
                if (!response.ok) {
                    if (response.status === 404) {
                        sessionSelect.innerHTML = '<option value="">Aucune session - Créez-en une</option>';
                        return;
                    }
                    throw new Error('Erreur serveur');
                }
                
                // Gérer les deux formats de réponse
                const data = await response.json();
                const sessions = Array.isArray(data) ? data : (data.value || []);
                
                sessionSelect.innerHTML = '<option value="">Choisir une session...</option>';
                
                if (sessions.length === 0) {
                    sessionSelect.innerHTML = '<option value="">Aucune session - Créez-en une</option>';
                    return;
                }
                
                sessions.forEach(session => {
                    const option = document.createElement('option');
                    option.value = session.session_id || session.session_uuid || session.id;
                    option.textContent = session.session_name || session.name;
                    sessionSelect.appendChild(option);
                });
                
                await loadActiveSession();
            } catch (error) {
                console.error('Error loading sessions:', error);
                sessionSelect.innerHTML = '<option value="">Erreur - Créez une nouvelle session</option>';
            }
        }
"""

# Chercher où insérer la fonction (après showMessage)
pattern = r"(function showMessage\([^}]+\}\s*\})"

match = re.search(pattern, content, re.DOTALL)

if match:
    insertion_point = match.end()
    new_content = content[:insertion_point] + "\n" + load_sessions_function + "\n" + content[insertion_point:]
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fonction loadSessions ajoutée avec succès !")
    print(f"   Position : après la fonction showMessage (caractère {insertion_point})")
    print(f"   Taille du fichier : {len(new_content)} caractères")
else:
    print("❌ Impossible de trouver le point d'insertion (fonction showMessage)")
    print("   Le fichier est peut-être trop corrompu.")
    print("\n📊 Statistiques du fichier :")
    print(f"   - Taille : {len(content)} caractères")
    print(f"   - 'function showMessage' trouvé : {'showMessage' in content}")
    print(f"   - 'loadSessions' trouvé : {'loadSessions' in content}")
