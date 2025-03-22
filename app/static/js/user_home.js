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









// Js for handling the disappearing animation of the item from the user home page
document.addEventListener('DOMContentLoaded', function () {
    const countdownSpans = document.querySelectorAll('.time_left');

    function updateCountdown() {
        countdownSpans.forEach(span => {
            const expiration = new Date(span.dataset.expiration);
            const now = new Date();
            const diff = expiration - now;

            if (diff <= 0) {
                const card = span.closest('.card');
                const itemId = span.dataset.itemId;
                const currentBid = {{ item_bids | tojson }};

                // If item has a highest bid, animate and remove
                if (currentBid[itemId]) {
                    card.classList.add('fade-out');

                    setTimeout(() => {
                        const col = card.closest('.col');
                        if (col) col.remove();
                    }, 1000); // Match fadeOut animation duration
                } else {
                    // Otherwise, just show expired state
                    span.innerText = "Expired";
                    card.classList.add("expired-item");
                }
            } else {
                // Display remaining time
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                span.innerText = `${hours}h ${minutes}m ${seconds}s`;
            }
        });
    }

    setInterval(updateCountdown, 1000);
    updateCountdown(); // Initial run
});
