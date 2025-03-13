var socket = io();

function placeBid(itemId) {
    var bidAmount = document.getElementById("bid_amount").value;

    // Send bid to server via WebSocket
    socket.emit("new_bid", { 
        item_id: itemId, 
        bid_amount: bidAmount 
    });
}

// Listen for successful bids
socket.on("bid_success", function(data) {
    alert(data.message);  // Show success message
});

// Listen for bid errors
socket.on("bid_error", function(data) {
    alert(data.message);  // Show error message
});

// Live update the highest bid when a new bid is placed
socket.on("update_bid", function(data) {
    var highestBidElement = document.getElementById("highest_bid");
    if (highestBidElement && data.item_id == highestBidElement.dataset.itemId) {
        highestBidElement.innerText = "£" + data.new_bid;
    }
});
