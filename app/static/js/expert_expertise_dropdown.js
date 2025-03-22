document.getElementById("expertiseFilter").addEventListener("change", function () {
    const selected = this.value;
    const experts = document.querySelectorAll(".expert-entry");

    experts.forEach(expert => {
        if (selected === "all" || expert.dataset.expertise === selected) {
            expert.style.display = "";
        } else {
            expert.style.display = "none";
        }
    });
});

