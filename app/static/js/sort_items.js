document.addEventListener("DOMContentLoaded", function() {
    let sortDropdown = document.getElementById("items_dropdown"); // Make sure this matches the dropdown ID in HTML
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function() {
            let selected = this.value;

            fetch(`/user/sort_items?sort=${selected}`)
                .then(response => response.json() )
                .then(data => {
                    console.log("Fetch response received", data); // ✅ Check if response is correct
                    let container = document.getElementById("items_sort");
                    // Clear previous items
                    container.innerHTML = ""; 
                    
                    //data to sort by
                    data.forEach(item => {
                        let item_Element = document.createElement("div");
                        item_Element.className = "col item-card";
                        item_Element.dataset.itemId = item.item_id;
                        item_Element.dataset.price = item.minimum_price;
                        item_Element.dataset.name = item.item_name;
                        item_Element.dataset.description = item.description;
                        item_Element.dataset.shipping_cost = item.shipping_cost;

                        // what to print when sorted
                        item_Element.innerHTML = `
                            <div class="card h-100">
                                <img src="/static/images/items/${item.item_image}" class="card-img-top" alt="${ item.item_name }">
                                <div class="card-body">
                                    <h5 class="card-title">${ item.item_name }</h5>
                                    <p class="card-text">Description: ${ item.description }</p>
                                    <p class="card-text">Price: £${ item.minimum_price }</p>
                                    <p class="card-text">Shipping Price: £${ item.shipping_cost }</p>
                                    
                                    <a href="/user/item_details/${item.item_id}" class="btn btn-primary">
                                        View Details
                                    </a>
                    
                                    ${item.is_watched ? 
                                        `<span class="fa fa-heart selected" data-item-id="${item.item_id}"></span>
                                        <input type="hidden" name="watch" value="1">`
                                        : 
                                        `<span class="fa fa-heart" data-item-id="${item.item_id}"></span>
                                        <input type="hidden" name="watch" value="0">
                                    `}
                                </div>
                            </div>
                        `;
                        container.appendChild(item_Element);
                    });  
                })
                .catch(error => {
                    console.error('Error during fetch operation:', error);
                });
        });
    }   
});