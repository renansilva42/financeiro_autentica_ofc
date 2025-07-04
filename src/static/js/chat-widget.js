// Floating Chat Widget v1.0.0
// Author: Financeira Autêntica
// Este componente é autossuficiente: basta importar este arquivo em qualquer página
// <script src="{{ url_for('static', filename='js/chat-widget.js') }}" defer></script>
// Não é necessário nenhum CSS adicional, pois os estilos são injetados automaticamente.

(() => {
    // Evitar múltiplas instâncias
    if (window.__CHAT_WIDGET_LOADED__) return;
    window.__CHAT_WIDGET_LOADED__ = true;

    // -------------------- Configurações --------------------
    const CONFIG = {
        primaryColor: '#0d6efd',   // Azul bootstrap padrão
        accentColor: '#ffffff',   // Cor dos ícones e texto
        zIndex: 9999,             // Garantir que fique sobreposto
        welcomeMessage: 'Olá! Como podemos ajudar?'
    };

    // -------------------- CSS ------------------------------
    const styleContent = `
        :root {
            --chat-primary: ${CONFIG.primaryColor};
            --chat-accent: ${CONFIG.accentColor};
        }
        #chat-widget-container {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: ${CONFIG.zIndex};
            font-family: "Roboto", "Helvetica Neue", Helvetica, Arial, sans-serif;
        }
        #chat-bubble {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--chat-primary);
            color: var(--chat-accent);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        #chat-bubble:hover {
            transform: scale(1.05);
        }
        #chat-bubble i {
            font-size: 1.5rem;
        }
        #chat-window {
            width: 320px;
            max-width: 90vw;
            height: 420px;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: absolute;
            bottom: 80px; /* altura do bubble + espaçamento */
            right: 0;
            opacity: 0;
            visibility: hidden;
            transform: translateY(20px);
            transition: all 0.3s ease;
        }
        #chat-window.open {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }
        .chat-header {
            background: var(--chat-primary);
            color: var(--chat-accent);
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .chat-header span {
            font-weight: 600;
        }
        .chat-close {
            background: transparent;
            border: none;
            color: var(--chat-accent);
            font-size: 1.25rem;
            cursor: pointer;
        }
        .chat-body {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 0.75rem;
            display: flex;
            max-width: 80%;
        }
        .message.bot {
            justify-content: flex-start;
        }
        .message.user {
            justify-content: flex-end;
        }
        .message .bubble {
            padding: 0.5rem 0.75rem;
            border-radius: 18px;
            font-size: 0.875rem;
            line-height: 1.2rem;
        }
        .message.bot .bubble {
            background: #e9ecef;
            color: #212529;
            border-bottom-left-radius: 0;
        }
        .message.user .bubble {
            background: var(--chat-primary);
            color: var(--chat-accent);
            border-bottom-right-radius: 0;
        }
        .chat-input {
            display: flex;
            padding: 0.75rem 0.5rem;
            border-top: 1px solid #dee2e6;
            background: #ffffff;
        }
        .chat-input input {
            flex: 1;
            border: 1px solid #ced4da;
            border-radius: 20px;
            padding: 0.4rem 0.9rem;
            font-size: 0.875rem;
            outline: none;
        }
        .chat-input button {
            border: none;
            background: var(--chat-primary);
            color: var(--chat-accent);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-left: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.2s;
        }
        .chat-input button:hover {
            background: #0b5ed7; /* bootstrap darker */
        }
        /* Scrollbar custom (webkit) */
        .chat-body::-webkit-scrollbar {
            width: 6px;
        }
        .chat-body::-webkit-scrollbar-thumb {
            background: rgba(0,0,0,0.1);
            border-radius: 3px;
        }
    `;

    const styleTag = document.createElement('style');
    styleTag.id = 'chat-widget-styles';
    styleTag.textContent = styleContent;
    document.head.appendChild(styleTag);

    // -------------------- HTML -----------------------------
    const container = document.createElement('div');
    container.id = 'chat-widget-container';
    container.innerHTML = `
        <div id="chat-bubble" aria-label="Abrir chat" tabindex="0">
            <i class="bi bi-chat-dots-fill"></i>
        </div>
        <div id="chat-window" aria-label="Janela de chat">
            <div class="chat-header">
                <span>Chat de Suporte</span>
                <button class="chat-close" aria-label="Fechar chat"><i class="bi bi-x-lg"></i></button>
            </div>
            <div class="chat-body" id="chat-messages"></div>
            <form class="chat-input" id="chat-form">
                <input type="text" id="chat-input-field" placeholder="Digite sua mensagem..." autocomplete="off" required />
                <button type="submit" aria-label="Enviar mensagem"><i class="bi bi-send-fill"></i></button>
            </form>
        </div>
    `;
    document.body.appendChild(container);

    const bubbleButton  = container.querySelector('#chat-bubble');
    const chatWindow    = container.querySelector('#chat-window');
    const closeButton   = container.querySelector('.chat-close');
    const messagesArea  = container.querySelector('#chat-messages');
    const form          = container.querySelector('#chat-form');
    const inputField    = container.querySelector('#chat-input-field');

    // --------------- Funções utilitárias -------------------
    const toggleChat = () => {
        chatWindow.classList.toggle('open');
        // Focar no input ao abrir
        if (chatWindow.classList.contains('open')) {
            setTimeout(() => inputField.focus(), 250);
        }
    };

    const appendMessage = (text, sender = 'bot') => {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${sender}`;
        messageEl.innerHTML = `<div class="bubble">${text}</div>`;
        messagesArea.appendChild(messageEl);
        messagesArea.scrollTop = messagesArea.scrollHeight;
    };

    // --------------- Eventos -------------------------------
    bubbleButton.addEventListener('click', toggleChat);
    bubbleButton.addEventListener('keypress', (e) => { if (e.key === 'Enter') toggleChat(); });
    closeButton.addEventListener('click', toggleChat);

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = inputField.value.trim();
        if (!text) return;
        appendMessage(text, 'user');
        inputField.value = '';
        // Simular resposta
        setTimeout(() => {
            appendMessage('Recebemos sua mensagem! Em breve responderemos.');
        }, 800);
    });

    // Mensagem de boas-vindas
    appendMessage(CONFIG.welcomeMessage);
})();
