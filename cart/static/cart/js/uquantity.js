$(document).ready(function() {
    $('.epd').each( function () {
        var quantity=+$(this).find('td.quantity').text();
        $(this).find('select').val(quantity);
        });
    $('.updateQuantity').change(function () {
        var amount = +$(this).val();
        var pid = +$(this).closest('tr').find('td.pid').text();
        
        var price = +$(this).closest('tr').find('td.price').text();
        var result = amount * price;
        $(this).closest('tr').find('td.total').html(result).show();
        $.ajax({
            url:  `http://127.0.0.1:8000/cart/cquantity/${pid}/${amount}/`,
            type:  'post',
            dataType:  'json',
            success:  function (data) {
                console.log(data.subtotal)
                $('.subtotal').text(data.subtotal);
                $('.cartnumber').text(data.cartQuantity);
                
            }
        });
    });
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken",getCookie('csrftoken'));
            }
        }
    });



});

