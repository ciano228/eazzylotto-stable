import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Erreur API:', error);
    return Promise.reject(error);
  }
);

export const lotteryAPI = {
  // Créer un nouveau tirage
  createDraw: (drawData) => api.post('/lottery/draws', drawData),
  
  // Récupérer tous les tirages
  getDraws: (limit = 20) => api.get(`/lottery/draws?limit=${limit}`),
  
  // Récupérer un tirage spécifique
  getDraw: (drawId) => api.get(`/lottery/draws/${drawId}`),
  
  // Supprimer un tirage
  deleteDraw: (drawId) => api.delete(`/lottery/draws/${drawId}`),
};

export const analysisAPI = {
  // Analyser un tirage
  analyzeDraw: (drawId, universe = null) => {
    const url = universe 
      ? `/analysis/draw/${drawId}?universe=${universe}`
      : `/analysis/draw/${drawId}`;
    return api.get(url);
  },
  
  // Obtenir le journal statistique
  getStatisticalJournal: (universe = null, limit = 50) => {
    let url = `/analysis/journal?limit=${limit}`;
    if (universe) {
      url += `&universe=${universe}`;
    }
    return api.get(url);
  },
  
  // Obtenir les fréquences
  getFrequencies: (universe = null, limit = 100) => {
    let url = `/analysis/frequencies?limit=${limit}`;
    if (universe) {
      url += `&universe=${universe}`;
    }
    return api.get(url);
  },
  
  // Obtenir les univers disponibles
  getUniverses: () => api.get('/analysis/universes'),
  
  // Obtenir les informations d'une combinaison
  getCombinationInfo: (num1, num2) => api.get(`/analysis/combinations/${num1}/${num2}`),
};

export default api;