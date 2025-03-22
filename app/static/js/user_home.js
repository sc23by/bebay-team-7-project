const current_user_id = {{ current_user.id | tojson }};


socket.on('auction_ended', function(data) {
    const itemId = data.item_id;
    const winnerId = data.winner_id;

    // If the current user is the winner
    if (current_user_id === winnerId) {
        const itemCard = document.querySelector(`[data-item-id="${itemId}"]`)?.closest('.col');

        if (itemCard) {
            // Add the animation class
            itemCard.classList.add('fly-out');

            // Remove it from the DOM after animation completes
            setTimeout(() => {
                itemCard.remove();
            }, 600); // Matches CSS animation duration
        }
    }
});







