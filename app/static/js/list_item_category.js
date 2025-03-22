document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("category-select");
    if (!select) return;

    const updateColor = () => {
        select.style.color = select.value === "" ? "#6c757d" : "#212529";
    };

    updateColor(); // run once on load
    select.addEventListener("change", updateColor);
});
