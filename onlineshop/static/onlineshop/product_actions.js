$(document).ready(function () {

    var formfield = $('<div>').append($('<input class="notify-email" type="text">'),
                                      $('<button class="notify-confirm">').text('Ok')
                                    );

    $('.button').click( function (e) {
        var data = JSON.stringify($(this).data());
        var url = $(this).attr('href');
        $.post(url, data, function(msg) {
            alert(msg["message"]);
        }).fail(function(msg) {
             alert(msg.responseJSON["message"]) 
            });
        e.preventDefault();
    });

    $('.notifyme').click( function(e) {
        var link = $(this);
        var productId = $(this).data('product');
        var url = $(this).attr('href');
        $(this).parent().append(formfield);
        $('.notify-confirm').click( function(e) {
            var email = $('.notify-email').val();
            var data = JSON.stringify({"product": productId, "email": email});
            $.post(url, data, function(msg) {
                alert(msg["message"]);
                formfield.hide();
                link.text("Мы отправим вам уведомление :)")
            }).fail(function(msg) {
                alert(msg.responseJSON["message"])
            });
            e.preventDefault();
        })
        e.preventDefault();
    });
});