function validateBillingForm() {
    var ret = true;
    var fields = ['#id_b_phone', '#id_b_first_name', '#id_b_last_name', '#id_b_address', '#id_b_city', '#id_b_zip', '#id_email'];
    if ($('#check-ship-to-diff').is(":checked")) {
        fields.push('#id_s_phone', '#id_s_first_name', '#id_s_last_name', '#id_s_address', '#id_s_city', '#id_s_zip');
    }
    $.each(fields, function (a, i) {
        if ($(i).val() == '') {
            $(i).addClass('error');
            ret = false;
        } else {
            $(i).removeClass('error');
        }
        // postal code
        if (i == '#id_b_zip' || i == '#id_s_zip') {
            var zip_regex = /^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$/;
            if (!$(i).val().match(zip_regex)) {
                $(i).addClass('error');
                $(i).parent().find('p').remove();
                $(i).after('<p class="small text-danger">Please enter correct postal code.</p>');
                ret = false;
            } else {
                $(i).removeClass('error');
                $(i).parent().find('p').remove();
            }
        }
    });
    return ret;
}

function copyBillToShip() {
    if (!$('#check-ship-to-diff').is(":checked")) {
        $('input[name="ship_phone"]').val($('input[name="bill_phone"]').val())
        $('input[name="ship_first_name"]').val($('input[name="bill_first_name"]').val())
        $('input[name="ship_last_name"]').val($('input[name="bill_last_name"]').val())
        $('input[name="ship_company_name"]').val($('input[name="bill_company_name"]').val())
        $('select[name="ship_country"]').val($('select[name="bill_country"]').val()).change();
        $('input[name="ship_address_one"]').val($('input[name="bill_address_one"]').val())
        $('input[name="ship_city"]').val($('input[name="bill_city"]').val())
        $('select[name="ship_state_or_province"]').val($('select[name="bill_state_or_province"]').val()).change();
        $('input[name="ship_postal_code"]').val($('input[name="bill_postal_code"]').val())
    }
}

function createOrder() {
    ajax_loading_modal(true);
    $.ajax({
        url: '/ajax/create_order/',
        data: $('#form-checkout').serialize(),
        method: 'POST',
        async: false,
        beforeSend: function () {
            //ajax_loading_modal(true);
            //if(!$('.order-id').val().length){ return false; }
            //form.find('.btn-submit').attr('disabled', 'disabled');
        }
    }).always(function (e) {
        if (e['error'] === 0) {
            $('.order-id').val(e['order_id']);
            return true;
        }
        ajax_loading_modal(false);
        return false;
    });
}

$(function () {
    // CHANGE PROVINCE HANDLER
    $('.page-checkout #id_b_state').change(function () {
        ajax_loading_modal(true);
        $.get('/ajax/change_tax/', {
            total: $('#tas').val(),
            province: $(this).val(),
            code: $('#id_coupon_code').val()
        }, function (e) {
            if (e['error'] === 0) {
                $('#tax_perc').html(e['tax_perc']);
                $('#tax_doll').html(e['tax_doll']);
                $('#total').html(e['new_total']);
                $('#charge_total').val(e['new_total']);
            }
        }).always(function (e) {
            ajax_loading_modal(false);
        });
    });
    // COUPON CODE
    $('#btn-apply-code').click(function () {
        //ajax_loading_modal(true);
        $.get('/ajax/apply_code/', {total: $('#charge_total').val(), code: $('#ccode').val()}, function (e) {
            $('#ccode-success').html('');
            $('#ccode-error').html('');
            if (e['error'] === 0) {
                $('#ccode-success').html('Coupon code has been applied: -$' + e['discount'])
                $('#form-coupon').slideUp(500, function () {
                    $('#total').html(e['new_total']);
                    $('#charge_total').val(e['new_total']);
                    $('#id_coupon_code').val(e['code']);
                });
            } else {
                $('#ccode-error').html(e['message']);
            }
        }).always(function (e) {
            //ajax_loading_modal(false);
        });
    });
    // DIFF ADDRESS
    $('#check-ship-to-diff').change(function () {
        if ($(this).is(":checked")) {
            $('#diff-addr-wrapper').show('slow');
        } else {
            $('#diff-addr-wrapper').slideUp();
        }
    });


    $('#btn-submit').click(function (e) {
        if (validateBillingForm()) {
            $('#form-checkout').submit();
        }
    });

    $('#form-checkout').submit(function (e) {
        copyBillToShip();
        return createOrder();
    });
});