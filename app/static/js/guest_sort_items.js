document.addEventListener("DOMContentLoaded", function() {
    updateCountdown();
    
    let guest_items_container = document.getElementById("guest_items_sort");
    let guest_sort_dropdown = document.getElementById("guest_items_dropdown");
    if (guest_sort_dropdown) {
        guest_sort_dropdown.addEventListener("change", function() {
            let selected = this.value;

            fetch(`/guest_sort_items?sort=${selected}`)
                .then(response => response.json())
                .then(data => {
                    // Clear previous items
                    guest_items_container.innerHTML = ""; 
                    
                    // Dynamically update sorted items
                    data.forEach(item => {
                        let item_Element = document.createElement("div");
                        item_Element.className = "col gallery";
                        item_Element.dataset.itemId = item.item_id;
                        item_Element.dataset.price = item.minimum_price;
                        item_Element.dataset.name = item.item_name;
                        item_Element.dataset.shipping_cost = item.shipping_cost;
                        item_Element.dataset.current_highest_bid = item.current_highest_bid;
                        item_Element.dataset.expiration = item.expiration_time;
                        item_Element.dataset.time_left = item.time_left;
                        item_Element.dataset.seller_id = item.seller_id;

                        let highest_bid = item.current_highest_bid !== "None" 
                            ? `£${item.current_highest_bid}` 
                            : "No bids yet";

                        // Default empty like_button
                        let like_button = "";

                        let expired_item = item.time_left <= 0 ? "expired-item" : "";
                        console.log()
                        item_Element.innerHTML = `
                            <div class="card h-100 ${expired_item}">
                                    <img src="/static/images/items/${item.item_image}" class="card-img-top" alt="${item.item_name}">
                                    ${like_button}
                                    <div class="card-body">
                                        <h5 class="card-title">${item.item_name}</h5>
                                        <p class="card-text">Starting Price: £${item.minimum_price}</p>
                                        <p class="card-text">Current Highest Bid: ${highest_bid}</p>
                                        <p class="countdown">Time Left: 
                                            <span class="time_left"
                                                data-item-id="${item.item_id}"
                                                data-expiration="${item.expiration_time}">
                                            </span>
                                        </p> 
                                        <p class="card-text shipping">Shipping Price: £${item.shipping_cost}</p>                       
                                        ${item.approved ? `<span class="badge bg-success">Approved</span>` : ""}
                                        <a href="/register" class="btn btn-primary">
                                            View Details
                                        </a>
                                    </div>
                            </div>
                        `;
                        
                        guest_items_container.appendChild(item_Element);
                    });
                    updateCountdown();
                });
        });
    }
});