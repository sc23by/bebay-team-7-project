document.addEventListener("DOMContentLoaded", function() {
    let sortDropdown = document.getElementById("items_dropdown"); // Make sure this matches the dropdown ID in HTML
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function() {
            let selected = this.value;

            fetch(`/user/sort_items?sort=${selected}`)
                .then(response => response.json() )
                .then(data => {
                    let container = document.getElementById("items_sort");
                    // Clear previous items
                    container.innerHTML = ""; 
                    
                    //data to sort by
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

                        updateCountdown();

                        let highest_bid = item.current_highest_bid !== null 
                            ? `£${item.current_highest_bid}` 
                            : "No bids yet";

                        let expired_item = item.time_left <= 0 ? "expired-item" : "";

                        let like_button = item.seller_id !== current_user_id ? `
                            <span class="fa fa-heart ${item.is_watched ? 'selected' : ''}" 
                                data-item-id="${item.item_id}">
                            </span>
                            <input type="hidden" name="watch" value="${item.is_watched ? '1' : '0'}">
                        ` : "";

                        // what to print when sorted
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
                                                data-item-id=${ item.item_id }"
                                                data-expiration="${ item.expiration_time }">
                                            </span>
                                        </p> 
                                        <p class="card-text shipping">Shipping Price: £${ item.shipping_cost }</p>                       
                                        ${item.approved ? `<span class="badge bg-success">Approved</span>` : ""}
                                        <a href="/user/item_details/${item.item_id}" class="btn btn-primary">
                                            View Details
                                        </a>
                                    </div>
                            </div>
                        `;
                        container.appendChild(item_Element);
                    });  
                })
        });
    }   
});