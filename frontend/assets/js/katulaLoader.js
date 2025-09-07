// Module de chargement des données Katula
export async function loadUniverseData(universe, API_BASE) {
    console.log(`Chargement de ${universe}...`);
    
    try {
        // Charger formes seulement
        const formesRes = await fetch(`${API_BASE}/formes/real/${universe}`);
        const table = { status: 'simulated' };
        const formes = formesRes.ok ? await formesRes.json() : { 
            formes: ['carre', 'triangle', 'cercle', 'rectangle'] 
        };

        // Charger les détails de tous les chips en parallèle
        const chipDetails = {};
        const chipPromises = Array.from({ length: 48 }, (_, i) => {
            const chipNum = i + 1;
            return fetch(`${API_BASE}/formes/real/${universe}/chip/${chipNum}`)
                .then(res => res.ok ? res.json() : { formes_data: {} })
                .then(data => chipDetails[chipNum] = data)
                .catch(() => chipDetails[chipNum] = { formes_data: {} });
        });

        await Promise.all(chipPromises);

        console.log(`${universe} chargé avec succès`);
        return { table, formes, chipDetails, universe };

    } catch (error) {
        console.error(`Erreur chargement ${universe}:`, error);
        throw error;
    }
}