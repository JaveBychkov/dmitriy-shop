$(document).ready(function () {
    $('.button').click( function (e) {
        var data = JSON.stringify($(this).data());
        var url = $(this).attr('href');
        $.post(url, data, function(msg) {
            alert(msg["message"]);
        }).fail(function(msg) {
             alert(msg.responseJSON["message"]) 
            });
        e.preventDefault()
    });
});