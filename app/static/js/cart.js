// Handles subtotal calculation and Stripe checkout for selected auction items in the cart
function updateSubtotal() {
    const checkboxes = document.querySelectorAll(".item-checkbox:checked");
    let subtotal = 0;
    checkboxes.forEach(cb => {
        subtotal += parseFloat(cb.dataset.price);
    });
    document.getElementById("selected-subtotal").innerText = `£${subtotal.toFixed(2)}`;
}

document.addEventListener("DOMContentLoaded", function () {
    updateSubtotal(); // initial subtotal
    document.querySelectorAll(".item-checkbox").forEach(cb => {
        cb.addEventListener("change", updateSubtotal);
    });
});

document.getElementById("checkout-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const selectedCheckboxes = document.querySelectorAll(".item-checkbox:checked");
    const selectedItemIds = Array.from(selectedCheckboxes).map(cb => parseInt(cb.value));

    if (selectedItemIds.length === 0) {
        alert("Please select at least one item to pay for.");
        return;
    }

    fetch("/pay_selected", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ item_ids: selectedItemIds })
    })
    .then(res => res.json())
    .then(data => {
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            alert("Payment Error: " + data.error);
        }
    });
});