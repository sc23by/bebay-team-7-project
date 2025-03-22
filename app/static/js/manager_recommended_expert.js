function selectItem(itemId) {
    document.getElementById("selectedItemId").value = itemId;

    const selectedInput = document.querySelector(`input[name="selected_item"][value="${itemId}"]`);
    const selectedCategory = selectedInput.getAttribute("data-category");

    const expertEntries = document.querySelectorAll(".expert-entry");
    expertEntries.forEach(entry => {
        const expertise = entry.getAttribute("data-expertise");

        const oldBadge = entry.querySelector(".recommended-badge");
        if (oldBadge) oldBadge.remove();

        if (expertise === selectedCategory) {
            const badge = document.createElement("span");
            badge.classList.add("badge", "bg-info", "ms-2", "recommended-badge");
            badge.textContent = "Recommended";
            entry.querySelector("label").appendChild(badge);
        }
    });
}

function updateAvailability(expertId) {
    const availabilityDropdown = document.getElementById("availabilityDropdown");
    const availabilityContainer = document.getElementById("availabilityContainer");

    availabilityDropdown.innerHTML = '<option value="">Select a time slot</option>';

    if (expertAvailability[expertId] && expertAvailability[expertId].length > 0) {
        expertAvailability[expertId].forEach(slot => {
            const option = document.createElement("option");
            option.value = slot.id;
            option.textContent = `${slot.date} - ${slot.start_time} (${slot.duration}h)`;
            availabilityDropdown.appendChild(option);
        });
        availabilityContainer.classList.remove("d-none");
    } else {
        availabilityContainer.classList.add("d-none");
    }
}

window.selectItem = selectItem;
window.updateAvailability = updateAvailability;
