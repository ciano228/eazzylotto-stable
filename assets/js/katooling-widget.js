/**
 * Widget KATOOLING - Composant réutilisable pour expliquer la méthode
 */

const KatoolingWidget = {
    // Générer le widget d'explication
    generateWidget: function(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const config = {
            showDemo: options.showDemo !== false,
            showSteps: options.showSteps !== false,
            compact: options.compact || false,
            ...options
        };

        const widgetHTML = `
            <div class="katooling-widget ${config.compact ? 'compact' : ''}">
                <div class="widget-header">
                    <div class="widget-icon">🔬</div>
                    <div class="widget-title">
                        <h3>Méthode KATOOLING</h3>
                        <p>Notre innovation révolutionnaire</p>
                    </div>
                </div>
                
                ${config.showDemo ? this.generateMiniDemo() : ''}
                
                <div class="widget-content">
                    <p class="widget-description">
                        <strong>KATOOLING</strong> transforme chaque combinaison de loto en coordonnées 
                        géométriques sur notre Table Katula 8x6, permettant de prédire les zones 
                        gagnantes futures avec une précision inégalée.
                    </p>
                    
                    ${config.showSteps ? this.generateMiniSteps() : ''}
                </div>
                
                <div class="widget-actions">
                    <a href="katooling-method.html" class="widget-button primary">
                        🔍 En savoir plus
                    </a>
                    <a href="katula-multi-universe.html" class="widget-button secondary">
                        🚀 Essayer maintenant
                    </a>
                </div>
            </div>
        `;

        container.innerHTML = widgetHTML;
        this.addWidgetStyles();
        this.initWidgetInteractions();
    },

    // Générer une mini démo de la table
    generateMiniDemo: function() {
        return `
            <div class="mini-katula-demo">
                <div class="mini-table">
                    ${Array.from({length: 24}, (_, i) => 
                        `<div class="mini-cell" data-cell="${i + 1}">${i + 1}</div>`
                    ).join('')}
                </div>
                <p class="demo-caption">Table Katula - Cliquez pour voir l'effet</p>
            </div>
        `;
    },

    // Générer les étapes simplifiées
    generateMiniSteps: function() {
        return `
            <div class="mini-steps">
                <div class="mini-step">
                    <span class="step-icon">🎲</span>
                    <span class="step-text">Tirage → Combinaisons</span>
                </div>
                <div class="mini-step">
                    <span class="step-icon">🗺️</span>
                    <span class="step-text">Classification → Position</span>
                </div>
                <div class="mini-step">
                    <span class="step-icon">🎯</span>
                    <span class="step-text">Analyse → Prédiction</span>
                </div>
            </div>
        `;
    },

    // Ajouter les styles du widget
    addWidgetStyles: function() {
        if (document.getElementById('katooling-widget-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'katooling-widget-styles';
        styles.textContent = `
            .katooling-widget {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border: 2px solid #ffd700;
                margin: 20px 0;
            }

            .katooling-widget.compact {
                padding: 15px;
            }

            .widget-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 20px;
            }

            .widget-icon {
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #1e3c72, #2a5298);
                color: #ffd700;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
            }

            .widget-title h3 {
                margin: 0;
                color: #1e3c72;
                font-size: 1.3rem;
                font-weight: 700;
            }

            .widget-title p {
                margin: 5px 0 0 0;
                color: #6c757d;
                font-size: 0.9rem;
            }

            .widget-description {
                color: #2c3e50;
                line-height: 1.6;
                margin-bottom: 20px;
            }

            .mini-katula-demo {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: center;
            }

            .mini-table {
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 3px;
                max-width: 300px;
                margin: 0 auto 10px;
            }

            .mini-cell {
                aspect-ratio: 1;
                background: #e9ecef;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.7rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .mini-cell:hover {
                background: #ffd700;
                color: #1e3c72;
                transform: scale(1.1);
            }

            .demo-caption {
                font-size: 0.8rem;
                color: #6c757d;
                margin: 0;
            }

            .mini-steps {
                display: flex;
                justify-content: space-between;
                gap: 10px;
                margin: 15px 0;
            }

            .mini-step {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 5px;
                flex: 1;
                text-align: center;
            }

            .step-icon {
                font-size: 1.2rem;
            }

            .step-text {
                font-size: 0.8rem;
                color: #6c757d;
                font-weight: 500;
            }

            .widget-actions {
                display: flex;
                gap: 10px;
                justify-content: center;
                flex-wrap: wrap;
            }

            .widget-button {
                padding: 10px 20px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                text-align: center;
            }

            .widget-button.primary {
                background: #1e3c72;
                color: white;
            }

            .widget-button.secondary {
                background: #ffd700;
                color: #1e3c72;
            }

            .widget-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }

            @media (max-width: 768px) {
                .mini-steps {
                    flex-direction: column;
                    gap: 15px;
                }

                .mini-step {
                    flex-direction: row;
                    justify-content: flex-start;
                    text-align: left;
                }

                .widget-actions {
                    flex-direction: column;
                }
            }
        `;

        document.head.appendChild(styles);
    },

    // Initialiser les interactions du widget
    initWidgetInteractions: function() {
        // Animation des cellules de la mini table
        document.querySelectorAll('.mini-cell').forEach(cell => {
            cell.addEventListener('click', function() {
                // Retirer les anciens highlights
                document.querySelectorAll('.mini-cell').forEach(c => c.classList.remove('highlighted'));
                
                // Ajouter le highlight
                this.classList.add('highlighted');
                this.style.background = '#ffd700';
                this.style.color = '#1e3c72';
                
                // Retirer après 2 secondes
                setTimeout(() => {
                    this.style.background = '';
                    this.style.color = '';
                    this.classList.remove('highlighted');
                }, 2000);
            });
        });

        // Animation d'introduction
        setTimeout(() => {
            const cells = document.querySelectorAll('.mini-cell');
            cells.forEach((cell, index) => {
                setTimeout(() => {
                    cell.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        cell.style.transform = '';
                    }, 200);
                }, index * 50);
            });
        }, 1000);
    },

    // Générer une notification KATOOLING
    showKatoolingTip: function(message) {
        const tip = document.createElement('div');
        tip.className = 'katooling-tip';
        tip.innerHTML = `
            <div class="tip-icon">🔬</div>
            <div class="tip-content">
                <strong>KATOOLING TIP:</strong> ${message}
            </div>
        `;

        // Ajouter les styles si nécessaire
        if (!document.getElementById('katooling-tip-styles')) {
            const tipStyles = document.createElement('style');
            tipStyles.id = 'katooling-tip-styles';
            tipStyles.textContent = `
                .katooling-tip {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, #1e3c72, #2a5298);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
                    z-index: 10000;
                    max-width: 300px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    animation: slideInUp 0.5s ease;
                }

                .tip-icon {
                    font-size: 1.5rem;
                    color: #ffd700;
                }

                .tip-content {
                    font-size: 0.9rem;
                    line-height: 1.4;
                }

                @keyframes slideInUp {
                    from {
                        transform: translateY(100px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(tipStyles);
        }

        document.body.appendChild(tip);

        // Retirer après 5 secondes
        setTimeout(() => {
            tip.style.animation = 'slideInUp 0.5s ease reverse';
            setTimeout(() => tip.remove(), 500);
        }, 5000);
    }
};

// Export global
window.KatoolingWidget = KatoolingWidget;