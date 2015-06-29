$(document).ready(function() {
    product_template = loadTemplate('#product-template');

    // Rendering all the products
    apiCall('/product', 'GET', {}, function(data) {
        renderProducts(data.result);
    });

    $('#fashion-query').on('keyup', function(e) {
        var $this = $('#fashion-query')
        var query = $this.val();

        var products = $('.fashion-products');
        if (!query) {
            products.find('li').show();
        }
        else {
            products.find('li').hide();
            products.find('li:contains(' + query + ')').show();
        }

    });

    $('.fashion-products').on('click', 'li', function() {
        $(this).siblings('li').removeClass('active');
        $(this).addClass('active');
    });


    var firstValidFrame = null
    changed=false;
    Leap.loop(function(frame) { 

       if (frame.valid) {
          if (!firstValidFrame) firstValidFrame = frame
          var t = firstValidFrame.translation(frame)

            //assign rotation coordinates
            transX = t[0]
            transY = t[1]
            if (transX > 200 && changed == false){
              console.log("haha")
              changed = true;
              window.location.replace("../");
              return;
            }
        }

  });


});

renderProducts = function(products) {
    $('.fashion-products').html('');
    $.each(['top', 'bottom', 'feet'], function(i, type) {
        console.log(products);
        $.each(products[type], function(i, p) {
            $('.fashion-products.' + type).append(product_template(p));
        });

        $('.fashion-products.' + type + ' li').eq(0).addClass('active');
    });

    $( '.slider' ).lemmonSlider();
    $( '.fashion-products' ).width(function(i, width) {
        return width * 2;
    })
}
