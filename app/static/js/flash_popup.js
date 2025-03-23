document.addEventListener("DOMContentLoaded", function() {
    let toastElList = [].slice.call(document.querySelectorAll(".toast"));
    toastElList.map(function(toastEl) {
    new bootstrap.Toast(toastEl).show();
    });
});
