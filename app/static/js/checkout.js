document.getElementById("checkout-button").addEventListener("click", function () {
    fetch("{{ url_for('create_checkout_session', item_id=item.item_id) }}", {
        method: "POST",
    })
    .then(response => response.json())
    .then(session => {
        window.location.href = session.url;
    })
    .catch(error => console.error("Error:", error));
});