async function showDrawDetails() {
    // Vérifier que les données sont  chargées
    if (!window.loadedDraws || window.loadedDraws.length === 0) {
        alert('❌ Aucun historique chargé.\n\nVeuillez d\'abord :\n1. Configurer et lancer l\'analyse\n2. Attendre le chargement automatique de l\'historique\n\nOu cliquez sur "🔄 Charger Historique Réel" pour forcer le chargement.');
        return;
    }

    // Récupérer l'univers sélectionné
    const selectedUniverse = currentAnalysisData?.universe || document.getElementById('universeSelect')?.value || 'mundo';

    // Afficher un loader
    const loaderModal = document.createElement('div');
    loaderModal.className = 'draw-history-modal';
    loaderModal.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); z-index: 10000; text-align: center;">
            <h3>🔄 Chargement des combinaisons détaillées...</h3>
            <p>Univers: <strong>${selectedUniverse.toUpperCase()}</strong></p>
            <p>Récupération des métadonnées pour ${window.loadedDraws.length} tirages</p>
        </div>
    `;
    document.body.appendChild(loaderModal);

    try {
        // Récupérer les combinaisons détaillées pour chaque tirage
        const combinationsDetails = [];

        for (const draw of window.loadedDraws) {
            // Skip no-draw et no-hold
            if (draw.is_no_draw || !draw.winning_numbers || draw.winning_numbers.length < 2) {
                continue;
            }

            // Générer toutes les combinaisons C(n,2)
            const numbers = draw.winning_numbers;
            for (let i = 0; i < numbers.length; i++) {
                for (let j = i + 1; j < numbers.length; j++) {
                    const num1 = numbers[i];
                    const num2 = numbers[j];

                    try {
                        // Appeler l'API pour obtenir les détails de la combinaison
                        const response = await fetch(`${window.location.origin}/journal/combination/${num1}/${num2}`);
                        if (response.ok) {
                            const result = await response.json();
                            if (result.success && result.data) {
                                const combo = result.data;

                                // Filtrer par univers sélectionné
                                if (combo.univers && combo.univers.toLowerCase() === selectedUniverse.toLowerCase()) {
                                    combinationsDetails.push({
                                        // Informations du tirage
                                        draw_date: draw.date,
                                        lottery_name: draw.loto_name || draw.name,
                                        draw_id: draw.id,
                                        period: draw.period || 'N/A',

                                        // Informations de la combinaison
                                        combination: combo.combination || `${num1}-${num2}`,
                                        denomination: combo.denomination || 'N/A',
                                        alpha_ranking: combo.alpha_ranking || 'N/A',
                                        chip: combo.chip || combo.chip_number || 'N/A',
                                        drawer: combo.drawer_name || combo.drawer || 'N/A',
                                        tome: combo.tome || 'N/A',
                                        petique: combo.petique || 'N/A',
                                        granque: combo.granque || 'N/A',
                                        ligne: combo.ligne || 'N/A',
                                        colonne: combo.colonne || 'N/A',
                                        parite: combo.parite || 'N/A',
                                        unidos: combo.unidos || 'N/A',
                                        forme: combo.forme || 'N/A',
                                        engine: combo.engine || 'N/A',
                                        beastie: combo.beastie || 'N/A',
                                        univers: combo.univers || selectedUniverse
                                    });
                                }
                            }
                        }
                    } catch (error) {
                        console.warn(`Erreur récupération combinaison ${num1}-${num2}:`, error);
                    }
                }
            }
        }

        // Fermer le loader
        loaderModal.remove();

        if (combinationsDetails.length === 0) {
            alert(`❌ Aucune combinaison trouvée pour l'univers ${selectedUniverse.toUpperCase()}\n\nVérifiez que:\n- L'univers sélectionné correspond aux tirages\n- Les combinaisons sont bien enregistrées dans la base de données`);
            return;
        }

        // Trier par date (plus récent en haut)
        combinationsDetails.sort((a, b) => {
            const dateA = new Date(a.draw_date);
            const dateB = new Date(b.draw_date);
            return dateB - dateA;
        });

        // Afficher le modal avec les combinaisons détaillées
        displayCombinationsModal(combinationsDetails, selectedUniverse);

    } catch (error) {
        loaderModal.remove();
        console.error('Erreur lors du chargement des détails:', error);
        alert('❌ Erreur lors du chargement des combinaisons détaillées.\n\nConsultez la console pour plus de détails.');
    }
}
