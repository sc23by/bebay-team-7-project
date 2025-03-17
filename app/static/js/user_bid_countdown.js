document.addEventListener("DOMContentLoaded", function() {
    var timeLeftElements = document.querySelectorAll(".time_left"); // Works for both single & multiple items

    function updateCountdown() {
        timeLeftElements.forEach(function(element) {
            var expirationTime = new Date(element.getAttribute("data-expiration")).getTime();
            var now = new Date().getTime();
            var timeRemaining = expirationTime - now;

            if (timeRemaining <= 0) {
                element.innerText = "Expired";
                return;
            }

            var days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
            var hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

            element.innerText = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        });
    }

    if (timeLeftElements.length > 0) {
        updateCountdown(); // Update immediately
        setInterval(updateCountdown, 1000); // Update every second
    }
    
    function sendExpirationNotification(itemId) {
        if (Notification.permission === "granted") {
            new Notification("Auction Ended", {
                body: `The auction for item #${itemId} has ended.`,
                icon: "/static/images/auction-icon.png" // Replace with your own icon
            });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification("Auction Ended", {
                        body: `The auction for item #${itemId} has ended.`,
                        icon: "/static/images/auction-icon.png"
                    });
                }
            });
        } else {
            alert(`The auction for item #${itemId} has ended!`);
        }
    }
});
