$(document).ready(function () {

        // Function to count total for products
        var sumTotal = function() {
            var prices = $(".price").map( function() {
                var price = parseFloat($(this).data("price-for-one"));
                var quantity = parseInt($(this).prev().val());
                var total = price * quantity;
                $(this).text("₽ " + total.toFixed(2));
                return total
            }).get();
            return prices
        };

        // Handler to calculate price for product on quantity change
        $(".quantity").change( function(e) {
            var url = $(".line").data("update");
            var data = $(this).data();
            var quantity = $(this).val();
            data["quantity"] = quantity
            data = JSON.stringify(data);
            $.post(url, data, function(msg) {
                var prices = sumTotal();
                var total = prices.reduce(function(a,b){return a+b}, 0)
                $('.total').text(total.toFixed(2));
            });
        });

        // Handler for removing item from card
        $(".remove").click( function(e) {
            var line = $(this).closest("div")
            var data = JSON.stringify($(this).data());
            var url = $(".line").data("remove");
            $.post(url, data, function(msg) {
                line.hide("slow", function() {
                    $(this).remove();
                    var prices = sumTotal();
                    var total = prices.reduce(function(a,b){return a+b}, 0)
                    $(".total").text(total.toFixed(2));
                });
            }).fail(function(msg) {
                    alert(msg.responseJSON["message"]) 
                });
            e.preventDefault();

        });

        // Product price changed confirmation handler
        $(".confirm").click( function(e) {
            var url = $(this).data("url");
            var data = JSON.stringify({"confirm": true})
            var message = $(this).parent();
            $.post(url, data, function(msg) {
                message.slideUp("fast", function() {
                    $(this).remove();
                });
            });
            e.preventDefault();
        });
    });