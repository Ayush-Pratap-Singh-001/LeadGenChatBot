function sendMessage(message = null) {
    const input = document.getElementById('user-input');
    const userMessage = message || input.value.trim();
    if (!userMessage) return;

    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += `<div class="message user-message">${userMessage}</div>`;
    if (!message) input.value = '';
    
    // Add loading indicator after user message
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading';
    loadingDiv.className = 'loading';
    loadingDiv.innerText = '...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    $.ajax({
        url: '/chat',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ message: userMessage }),
        success: function(data) {
            // Remove loading indicator
            const loading = document.getElementById('loading');
            if (loading) loading.remove();
            
            chatBox.innerHTML += `<div class="message bot-message">${data.response}</div>`;
            if (data.order) {
                showOrderConfirmation(data.order);
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        },
        error: function() {
            // Remove loading indicator on error
            const loading = document.getElementById('loading');
            if (loading) loading.remove();
            
            chatBox.innerHTML += `<div class="message bot-message">Sorry, something went wrong.</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    });
}

function toggleChat() {
    const chatPopup = document.getElementById('chatPopup');
    const chatBox = document.getElementById('chat-box');
    const botAvatar = document.querySelector('.bot-avatar');
    if (chatPopup.style.display === 'flex') {
        chatPopup.style.display = 'none';
        botAvatar.style.display = 'none';
    } else {
        chatPopup.style.display = 'flex';
        botAvatar.style.display = 'block';
        if (!sessionStorage.getItem('greeted')) {
            $.ajax({
                url: '/chat',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ message: "start" }),
                success: function(data) {
                    chatBox.innerHTML += `<div class="message bot-message">${data.response}</div>`;
                    sessionStorage.setItem('greeted', 'true');
                }
            });
        }
    }
}

function showOrderConfirmation(order) {
    const confirmation = document.getElementById('orderConfirmation');
    document.getElementById('orderDetails').innerText = `Product: ${order.product}, Price: Rs. ${order.price}. Your details are saved!`;
    confirmation.style.display = 'block';
}

function closeConfirmation() {
    document.getElementById('orderConfirmation').style.display = 'none';
}

document.querySelectorAll('.quick-shop').forEach(button => {
    button.addEventListener('click', function() {
        const product = this.getAttribute('data-product');
        const price = this.getAttribute('data-price');
        sendMessage(`I want to buy ${product} for Rs. ${price}`);
    });
});

document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});