/**
 * EazzyLotto Icon Generator
 * Génère des icônes SVG avec des boules de loto 3D
 */

const IconGenerator = {
    // Générer une icône SVG avec boules de loto
    generateSVGIcon: function(size = 64, includeRays = true) {
        const svg = `
            <svg width="${size}" height="${size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <!-- Gradients pour les boules -->
                    <radialGradient id="goldBall" cx="0.3" cy="0.3" r="0.7">
                        <stop offset="0%" stop-color="#ffd700"/>
                        <stop offset="70%" stop-color="#f39c12"/>
                        <stop offset="100%" stop-color="#d35400"/>
                    </radialGradient>
                    
                    <radialGradient id="blueBall" cx="0.3" cy="0.3" r="0.7">
                        <stop offset="0%" stop-color="#74b9ff"/>
                        <stop offset="70%" stop-color="#4facfe"/>
                        <stop offset="100%" stop-color="#2980b9"/>
                    </radialGradient>
                    
                    <radialGradient id="redBall" cx="0.3" cy="0.3" r="0.7">
                        <stop offset="0%" stop-color="#ff6b6b"/>
                        <stop offset="70%" stop-color="#ff4757"/>
                        <stop offset="100%" stop-color="#c0392b"/>
                    </radialGradient>
                    
                    <!-- Reflets -->
                    <radialGradient id="highlight" cx="0.3" cy="0.3" r="0.4">
                        <stop offset="0%" stop-color="rgba(255,255,255,0.8)"/>
                        <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
                    </radialGradient>
                    
                    <!-- Ombres -->
                    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                        <feDropShadow dx="2" dy="4" stdDeviation="3" flood-color="rgba(0,0,0,0.3)"/>
                    </filter>
                    
                    ${includeRays ? `
                    <!-- Rayons de lumière -->
                    <defs>
                        <path id="ray" d="M32,8 L34,28 L30,28 Z" fill="rgba(255,215,0,0.3)"/>
                    </defs>
                    ` : ''}
                </defs>
                
                <!-- Fond avec gradient -->
                <rect width="64" height="64" rx="12" fill="url(#background)"/>
                <defs>
                    <radialGradient id="background" cx="0.5" cy="0.3" r="0.8">
                        <stop offset="0%" stop-color="#1e3c72"/>
                        <stop offset="100%" stop-color="#0f1419"/>
                    </radialGradient>
                </defs>
                
                ${includeRays ? `
                <!-- Rayons de lumière -->
                <g transform="translate(32,32)">
                    <use href="#ray" transform="rotate(0)"/>
                    <use href="#ray" transform="rotate(45)"/>
                    <use href="#ray" transform="rotate(90)"/>
                    <use href="#ray" transform="rotate(135)"/>
                    <use href="#ray" transform="rotate(180)"/>
                    <use href="#ray" transform="rotate(225)"/>
                    <use href="#ray" transform="rotate(270)"/>
                    <use href="#ray" transform="rotate(315)"/>
                </g>
                ` : ''}
                
                <!-- Boule dorée (9) -->
                <circle cx="20" cy="25" r="12" fill="url(#goldBall)" filter="url(#shadow)"/>
                <circle cx="20" cy="25" r="4" fill="url(#highlight)"/>
                <text x="20" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-weight="900" font-size="8" fill="#2c3e50">9</text>
                
                <!-- Boule bleue (2) -->
                <circle cx="44" cy="39" r="12" fill="url(#blueBall)" filter="url(#shadow)"/>
                <circle cx="44" cy="39" r="4" fill="url(#highlight)"/>
                <text x="44" y="44" text-anchor="middle" font-family="Arial, sans-serif" font-weight="900" font-size="8" fill="white">2</text>
                
                <!-- Boule rouge (L) -->
                <circle cx="32" cy="50" r="8" fill="url(#redBall)" filter="url(#shadow)"/>
                <circle cx="32" cy="50" r="3" fill="url(#highlight)"/>
                <text x="32" y="54" text-anchor="middle" font-family="Arial, sans-serif" font-weight="900" font-size="6" fill="white">L</text>
            </svg>
        `;
        
        return svg;
    },

    // Générer un favicon
    generateFavicon: function() {
        const svg = this.generateSVGIcon(32, false);
        return `data:image/svg+xml;base64,${btoa(svg)}`;
    },

    // Générer une icône d'application
    generateAppIcon: function(size = 192) {
        const svg = this.generateSVGIcon(size, true);
        return `data:image/svg+xml;base64,${btoa(svg)}`;
    },

    // Créer un canvas avec l'icône pour téléchargement
    createIconCanvas: function(size = 512) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        // Fond gradient
        const gradient = ctx.createRadialGradient(size/2, size/3, 0, size/2, size/2, size);
        gradient.addColorStop(0, '#1e3c72');
        gradient.addColorStop(1, '#0f1419');
        
        // Dessiner le fond arrondi
        ctx.fillStyle = gradient;
        ctx.roundRect(0, 0, size, size, size/8);
        ctx.fill();
        
        // Dessiner les boules
        this.drawLottoBall(ctx, size * 0.3, size * 0.4, size * 0.15, '#ffd700', '9', '#2c3e50');
        this.drawLottoBall(ctx, size * 0.7, size * 0.6, size * 0.15, '#4facfe', '2', 'white');
        this.drawLottoBall(ctx, size * 0.5, size * 0.8, size * 0.1, '#ff4757', 'L', 'white');
        
        return canvas;
    },

    // Dessiner une boule de loto sur canvas
    drawLottoBall: function(ctx, x, y, radius, color, text, textColor) {
        // Ombre
        ctx.save();
        ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        ctx.shadowBlur = radius * 0.3;
        ctx.shadowOffsetX = radius * 0.1;
        ctx.shadowOffsetY = radius * 0.2;
        
        // Gradient de la boule
        const gradient = ctx.createRadialGradient(
            x - radius * 0.3, y - radius * 0.3, 0,
            x, y, radius
        );
        
        if (color === '#ffd700') {
            gradient.addColorStop(0, '#ffd700');
            gradient.addColorStop(0.7, '#f39c12');
            gradient.addColorStop(1, '#d35400');
        } else if (color === '#4facfe') {
            gradient.addColorStop(0, '#74b9ff');
            gradient.addColorStop(0.7, '#4facfe');
            gradient.addColorStop(1, '#2980b9');
        } else if (color === '#ff4757') {
            gradient.addColorStop(0, '#ff6b6b');
            gradient.addColorStop(0.7, '#ff4757');
            gradient.addColorStop(1, '#c0392b');
        }
        
        // Dessiner la boule
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Reflet
        const highlightGradient = ctx.createRadialGradient(
            x - radius * 0.3, y - radius * 0.3, 0,
            x - radius * 0.3, y - radius * 0.3, radius * 0.5
        );
        highlightGradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
        highlightGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        ctx.fillStyle = highlightGradient;
        ctx.beginPath();
        ctx.arc(x - radius * 0.3, y - radius * 0.3, radius * 0.4, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore();
        
        // Texte
        ctx.fillStyle = textColor;
        ctx.font = `900 ${radius * 0.6}px Arial, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, x, y);
    },

    // Injecter les icônes dans le document
    injectIcons: function() {
        // Favicon
        let favicon = document.querySelector('link[rel="icon"]');
        if (!favicon) {
            favicon = document.createElement('link');
            favicon.rel = 'icon';
            document.head.appendChild(favicon);
        }
        favicon.href = this.generateFavicon();
        
        // Apple touch icon
        let appleIcon = document.querySelector('link[rel="apple-touch-icon"]');
        if (!appleIcon) {
            appleIcon = document.createElement('link');
            appleIcon.rel = 'apple-touch-icon';
            document.head.appendChild(appleIcon);
        }
        appleIcon.href = this.generateAppIcon(180);
        
        // Manifest icon
        let manifestIcon = document.querySelector('link[rel="manifest"]');
        if (!manifestIcon) {
            manifestIcon = document.createElement('link');
            manifestIcon.rel = 'manifest';
            manifestIcon.href = '/manifest.json';
            document.head.appendChild(manifestIcon);
        }
    },

    // Télécharger une icône
    downloadIcon: function(size = 512, filename = 'eazzylotto-icon.png') {
        const canvas = this.createIconCanvas(size);
        canvas.toBlob(function(blob) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
};

// Polyfill pour roundRect si nécessaire
if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x, y, width, height, radius) {
        this.beginPath();
        this.moveTo(x + radius, y);
        this.lineTo(x + width - radius, y);
        this.quadraticCurveTo(x + width, y, x + width, y + radius);
        this.lineTo(x + width, y + height - radius);
        this.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        this.lineTo(x + radius, y + height);
        this.quadraticCurveTo(x, y + height, x, y + height - radius);
        this.lineTo(x, y + radius);
        this.quadraticCurveTo(x, y, x + radius, y);
        this.closePath();
    };
}

// Auto-injection des icônes
document.addEventListener('DOMContentLoaded', function() {
    IconGenerator.injectIcons();
});

// Export global
window.IconGenerator = IconGenerator;