function ajax_loading_modal(tf) {
    if (tf) {
        $('body').addClass("loading");
    } else {
        $('body').removeClass("loading");
    }
}

function change_cart_val_in_nav(v) {
    $('#cart-nav-val').html(Number(v).toFixed(2));
}

function change_cart_subtotal_in_bottom(v) {
    $('.total-box .cart-subtotal').html(Number(v).toFixed(2));
}

function change_cart_total_in_bottom(v) {
    $('.total-box .cart-total').html(Number(v).toFixed(2));
}
// ADD TO CART
function add_to_cart(product_id, qty) {
    ajax_loading_modal(true);
    $.get('/ajax/add_to_cart/', {product_id: product_id, qty: qty}, function (e) {
        if (e['error'] === 0) {
            change_cart_val_in_nav(e['total']);
            // Reset qty to 1
            $('.page-product .product-quantity').val(1); // TODO
        }
    }).always(function (e) {
        ajax_loading_modal(false);
    });
}

//REMOVE FROM CART
function remove_from_cart(el, product_id) {
    ajax_loading_modal(true);
    $.get('/ajax/remove_from_cart/', {product_id: product_id}, function (e) {
        if (e['error'] === 0) {
            $(el).closest('tr').fadeOut("fast", function () {
                $(this).remove();
                change_cart_val_in_nav(e['total']);
                change_cart_subtotal_in_bottom(e['total']);
                change_cart_total_in_bottom(e['total_and_shipping']);
                // If there are no more items, hide the table
                if (e['count'] == 0) {
                    $('.page-cart .cart-wr').html('<h1 class="text-center text-muted">The Cart Is Empty</h1>');
                }
            })
        }
    }).always(function (e) {
        ajax_loading_modal(false);
    });
}

// CHANGE QUANTITY
function product_change_quantity(product_id, qty) {
    ajax_loading_modal(true);
    $.get('/ajax/product_change_quantity/', {product_id: product_id, qty: qty}, function (e) {
        if (e['error'] === 0) {
            change_cart_val_in_nav(e['total']);
            change_cart_subtotal_in_bottom(e['total']);
            change_cart_total_in_bottom(e['total_and_shipping']);
            // Change input val with a val returned
            $('.cart-qty-input[data-id="' + product_id + '"]').val(e['item_qty']);
            // Change subtotal in item
            $('.cart-item-subtotal[data-id="' + product_id + '"]').html(Number(e['item_subtotal']).toFixed(2));
        }
    }).always(function (e) {
        ajax_loading_modal(false);
    });
}

function scrollToDiv(el) {
    $('html, body').animate({
        scrollTop: $(el).offset().top
    }, 1000);
}


$(function () {
    // NAV
    $("#btn-om").click(function () {
        $('.nav-top').slideToggle('fast', function () {
            // Animation complete.
        });
        return false;
    });
    // ADD PLUS BUTTONS
    if ($(window).width() < 768) {
        $('.nav-top li').has('ul').find('> a').after('<a class="nav-plus" href="javascript:void(0)"><i class="fa fa-plus"></i></a><div class="clearfix"></div>');
    }

    // OPEN SUBMENUS AND TOGGLE + TO -
    $('.nav-plus').click(function () {
        $(this).find('.fa').toggleClass('fa-minus fa-plus');
        $(this).closest('li').find('> ul').slideToggle('fast');
    });
    // MAKE LOAD MORE REVIEWS LINK CLICKABLE
    $('.accord a').click(function (e) {
        e.stopImmediatePropagation();
    });
    // ACCORDEON
    $('.accord').click(function () {
        $(this).find('.fa').toggleClass('fa-minus fa-plus');
        $(this).find('.acc-content').slideToggle('fast');
        return false;
    });
    // PROD REVIEWS LINK
    $('.link-prod-reviews').click(function () {
        $('.accord-reviews').find('.fa').removeClass('fa-plus').addClass('fa-minus');
        $('.accord-reviews').find('.acc-content').slideDown('fast');
        scrollToDiv('.accord-reviews');
        return false;
    });
    // ADD TO CART
    $('.btn-add-to-cart').click(function () {
        var qty = parseInt($('.page-product .product-quantity').val()); // TODO
        if (isNaN(qty)) {
            qty = 1;
        }
        add_to_cart($(this).data('id'), qty);
        $('.page-product .product-quantity').val(1);
        return false;
    });
    // REMOVE FROM CART
    $('.btn-remove-from-cart').click(function () {
        remove_from_cart(this, $(this).data('id'));
        return false;
    });
    // CHANGE QUANTITY
    $('.cart-qty-input').change(function () {
        product_change_quantity($(this).data('id'), $(this).val());
    });
    // FORM IN CONTACT PAGE
    $('#form-contact').submit(function (ev) {
        ev.preventDefault();
        var form = $(this);
        //ajax_loading_modal(true);
        $.ajax({
            url: '/ajax/send_contact_form/',
            data: form.serialize(),
            method: 'POST',
            beforeSend: function () {
                form.find('.btn-red').attr('disabled', 'disabled');
            }
        }).done(function (e) {
            if (e['error'] === 0) {
                form.fadeTo("slow", 0.15, function () {
                    $('.form-wr .f-success').fadeIn();
                });
            } else {
                form.fadeTo("slow", 0.15, function () {
                    $('.form-wr .f-error').fadeIn();
                });
            }
        }).fail(function () {
            form.fadeTo("slow", 0.15, function () {
                $('.form-wr .f-error').fadeIn();
            });
        }).always(function (e) {
            //ajax_loading_modal(false);
        });
    });
});