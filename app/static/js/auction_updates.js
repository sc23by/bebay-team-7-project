// Connect to WebSocket
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

// Listen for the `auction_ended` event from Flask
socket.on('auction_ended', function(data) {
    let itemId = data.item_id;
    let winnerId = data.winner_id;

    let message;
    if (winnerId) {
        message = `Auction for Item ID ${itemId} has ended. A winner has been declared!`;
    } else {
        message = `Auction for Item ID ${itemId} has ended with no winner.`;
    }

    // Show a notification pop-up
    showNotification(message);

    // Optionally, refresh the notifications page if the user is on it
    if (window.location.pathname === '/notifications') {
        location.reload();  // Reload the page to show new notifications
    }
});

// Function to show a temporary pop-up notification
function showNotification(message) {
    let notificationArea = document.getElementById('notification-area');

    if (!notificationArea) {
        notificationArea = document.createElement('div');
        notificationArea.id = 'notification-area';
        notificationArea.style.position = 'fixed';
        notificationArea.style.top = '10px';
        notificationArea.style.right = '10px';
        notificationArea.style.zIndex = '1000';
        document.body.appendChild(notificationArea);
    }

    let notification = document.createElement('div');
    notification.innerText = message;
    notification.style.background = 'rgba(0, 0, 0, 0.8)';
    notification.style.color = 'white';
    notification.style.padding = '10px';
    notification.style.margin = '5px';
    notification.style.borderRadius = '5px';

    notificationArea.appendChild(notification);

    // Remove notification after 5 seconds
    setTimeout(() => notification.remove(), 5000);
}
