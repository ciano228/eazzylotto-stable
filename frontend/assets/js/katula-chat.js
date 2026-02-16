/**
 * Neuro-Katula Chat Assistant Logic
 * Handles communication with the AI Analyst API.
 */

window.toggleChat = function () {
    const chat = document.getElementById('neuroKatulaChat');
    chat.classList.toggle('collapsed');

    // Stop attention seeker when opening
    if (!chat.classList.contains('collapsed')) {
        chat.classList.remove('chat-attention-seeker');
        if (window.attentionTimeout) clearTimeout(window.attentionTimeout);
    }
};

window.initAttentionSeeker = function () {
    // Pulse every 60 seconds if collapsed
    setInterval(() => {
        const chat = document.getElementById('neuroKatulaChat');
        if (chat && chat.classList.contains('collapsed')) {
            chat.classList.add('chat-attention-seeker');

            // Remove class after 4s (2 pulses)
            window.attentionTimeout = setTimeout(() => {
                chat.classList.remove('chat-attention-seeker');
            }, 4000);
        }
    }, 60000);

    // Trigger first pulse after 10s
    setTimeout(() => {
        const chat = document.getElementById('neuroKatulaChat');
        if (chat && chat.classList.contains('collapsed')) {
            chat.classList.add('chat-attention-seeker');
            setTimeout(() => chat.classList.remove('chat-attention-seeker'), 4000);
        }
    }, 10000);
};

// Start attention seeker
document.addEventListener('DOMContentLoaded', () => {
    window.initAttentionSeeker();
});

window.handleChatKey = function (event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
};

window.sendChatMessage = async function () {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    const sessionId = document.getElementById('sessionSelect')?.value;
    const universe = document.getElementById('universe')?.value || 'mundo';
    const provider = document.getElementById('aiProviderSelect')?.value || 'deepseek';

    if (!message) return;

    // Add user message to UI
    appendMessage('user', message);
    input.value = '';

    try {
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                context: {
                    prediction_id: null, // Could be linked if needed
                    universe: universe,
                    session_id: sessionId, // Custom addition for journal context
                    provider: provider
                }
            })
        });

        if (response.ok) {
            const data = await response.json();
            appendMessage('ai', data.text, data.actions);
        } else {
            const error = await response.json();
            appendMessage('ai', `Désolé, j'ai rencontré une erreur : ${error.detail || 'Erreur inconnue'}`);
        }
    } catch (error) {
        console.error('Chat error:', error);
        appendMessage('ai', "Désolé, une erreur de connexion s'est produite.");
    }
};

function appendMessage(type, text, actions = []) {
    const chatMessages = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');

    if (actions.length > 0) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'chat-actions';
        actions.forEach(action => {
            const chip = document.createElement('span');
            chip.className = 'action-chip';
            chip.textContent = action;
            chip.onclick = () => {
                document.getElementById('chatInput').value = action;
                sendChatMessage();
            };
            actionsDiv.appendChild(chip);
        });
        msgDiv.appendChild(actionsDiv);
    }

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
