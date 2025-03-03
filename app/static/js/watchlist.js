$(document).ready(function () {

    // Colours heart with hover and removes colour when mouse is moved
    $(".fa-heart").on("mouseover", function () {
        var hover_obj = $(this);

        hover_obj.addClass("hover").nextAll().addClass("hover");
    }).on("mouseout", function () {
        $(".fa-heart").removeClass("hover");
    });

});