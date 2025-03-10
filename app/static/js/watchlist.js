$(document).ready(function () {

    // Set the CSRF token so not rejected by server
    var csrf_token = $('meta[name=csrf-token]').attr('content');

    // Configure ajaxSetup
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // Attach a function to trigger when heart is clicked
    $(".fa-heart").on("click", function () {
        var clicked_obj = $(this);

        // gets value of heart, either 1 or 0
        var watch = clicked_obj.attr('data-value') === "1" ? 0 : 1;
        clicked_obj.attr('data-value', watch);

        // applies class to show heart has been clicked
        clicked_obj.toggleClass("selected", watch === 1)

        // gets value of item id that was liked
        var item_id = clicked_obj.data('item-id');

        $.ajax({
            url: '/user/watch',
            type: 'POST',
            data: JSON.stringify({ item_id: item_id, watch: watch }),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                console.log("✅ AJAX success: ", response);
            },
        });

    });

    // Colours heart with mouse hover and removes colour when mouse is moved
    $(".fa-heart").on("mouseover", function () {
        var hover_obj = $(this);

        hover_obj.addClass("hover").nextAll().addClass("hover");
    }).on("mouseout", function () {
        $(".fa-heart").removeClass("hover");
    });

});