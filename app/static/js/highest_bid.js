document.getElementById("bid-form").addEventListener("submit", function(event) {
    // Prevent default form submission
    event.preventDefault();  
    
    let bid_Amount = document.getElementById("bid_amount").value;
    let item_Id = "{{ item.item_id }}";

    fetch(`/place_bid/${item_Id}`, {
        method: "POST",
        body: new FormData(this),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById("highest-bid").innerText = data.new_highest_bid;
        }
    })
    .catch(error => console.error("Error:", error));
});
