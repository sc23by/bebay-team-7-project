document.addEventListener("DOMContentLoaded", function () {
    let auctionData = document.getElementById("auction-data");
    console.log(auctionData)
    let timeLeftUrl = auctionData.getAttribute("data-time-left-url");
    let payNowUrl = auctionData.getAttribute("data-pay-now-url");
    let shippingCost = parseFloat(auctionData.getAttribute("data-shipping-cost"));
    let highestBid = parseFloat(auctionData.getAttribute("data-highest-bid"));
    
    function updateTimeLeft() {

        fetch(timeLeftUrl)
        .then(response => response.json())
        .then(data => {
            let timeLeftElement = document.getElementById("time-left");
            let payNowButton = document.getElementById("pay-now");

            if (data.time_left === "Expired") {
                timeLeftElement.innerHTML = "Expired";

                // Show Pay Now button immediately if it exists
                if (payNowButton) {
                    payNowButton.style.display = "block";
                }
            } else {
                timeLeftElement.innerHTML = data.time_left;
            }
        });
    }

    // Run the time check immediately on page load
    updateTimeLeft();

    // Reduce delay: Update countdown every 500ms instead of 1000ms
    setInterval(updateTimeLeft, 500);

    // Pay Now button functionality
    document.getElementById("pay-now")?.addEventListener("click", function () {
        let totalPrice = highestBid + shippingCost;

        fetch(payNowUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ total_price: totalPrice })
        })
        .then(response => response.json())
        .then(data => {
            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            } else {
                alert("Payment Error: " + data.error);
            }
        });
        // When the user navigates to the current page
    });
});
