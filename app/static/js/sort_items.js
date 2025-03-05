document.getElementById("sort_dropdown").addEventListener("change", function() {
    let selected = this.value;
    console.log("Dropdown changed! Selected:", selected); // ✅ Check if the event is detected

    fetch(`/user/sort?sort=${selected}`)
        .then(response => {
            console.log("Fetch response received", response); // ✅ Check if a response is received
                return response.json();
            })
        .then(data => {
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

                // what to print when sorted
                item_Element.innerHTML = `
                    <div class="card h-100">
                            <img src="/static/images/items/${item.item_image}" class="card-img-top" alt="${item.item_name}">
                            <div class="card-body">
                                <h5 class="card-title">${item.item_name}</h5>
                                <p class="card-text">Start Time: ${item.date_time}</p>
                                <p class="card-text">Price: £${item.minimum_price}</p>
                                <input type="button" value="Bid">
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
        .catch(error => console.error("Error fetching sorted data:", error));
});