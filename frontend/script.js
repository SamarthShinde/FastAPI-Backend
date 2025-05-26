document.addEventListener('DOMContentLoaded', function() {
    const inputElement = document.getElementById('message-input');
    const chatArea = document.querySelector('.chat-area'); 
    const sendButton = document.getElementById('send-button');

    function sendMessage() {
        const message = inputElement.value.trim();
        if (message) {
            const loadingIndicator = document.createElement('div');
            loadingIndicator.classList.add('loading');
            chatArea.appendChild(loadingIndicator);
            chatArea.scrollTop = chatArea.scrollHeight;

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.remove();
                addMessageToChat(message, 'user');
                addMessageToChat(data.response, 'bot');
            })
            .catch(error => {
                loadingIndicator.remove();
                console.error('Error:', error);
                addMessageToChat('Error sending message.', 'bot');
            });

            inputElement.value = ''; 
        }
    }

    function addMessageToChat(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chatArea.appendChild(messageElement);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    sendButton.addEventListener('click', sendMessage);
});