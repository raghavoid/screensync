document.addEventListener('DOMContentLoaded', () => {
    const roomId = JSON.parse(document.getElementById('room-id').textContent); // Ensure room ID is passed to the template
    const chatInput = document.getElementById('chat-input');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');

    const wsUrl = `ws://${window.location.host}/ws/room/${roomId}/`;
    const chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = () => {
        console.log('WebSocket connection established.');
    };

    chatSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', data.username === 'You' ? 'own' : 'other');
            messageElement.textContent = `${data.username}: ${data.message}`;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };

    chatSocket.onclose = (event) => {
        console.error('WebSocket connection closed:', event);
    };

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                type: 'message',
                message: message,
            }));
            chatInput.value = '';
        }
    });
});