
function parse_answer(result) {
    if ('data' in result) {
        for (k in result.data) {
            // console.log('data parse_answer:', k, '', result.data[k]);
            save_storage(k, result.data[k]);
        }

    }

    if ('dom' in result) {

        jQuery.each(result.dom, function (index, item) {
            // do something with `item` (or `this` is also `item` if you like)
            elem = $(item.selector);
            if (elem) {
                if ('html' in item)
                    $(elem).html(item.html);
                if ('css_add' in item)
                    jQuery.each(item.css_add, function (index, item) {
                        $(elem).addClass(item);
                    });
                if ('css_remove' in item)
                    jQuery.each(item.css_remove, function (index, item) {
                        $(elem).removeClass(item);
                    });
            }

        });
    }
}
function send_data(data) {

    fetch('/parse_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json()).then(result => {
        // console.log('Server response:', result);
        parse_answer(result);
    }
    ).catch(error => {
        console.error('Error:', error);
    }
    );
}
function init() {
    let data = {
        'lang': load_storage('lang', 0),
        'city1': load_storage('city1', ''),
        'city2': load_storage('city2', ''),
        'sender': 0
    }
    send_data(data);
    $('#city1').val(data.city1);
    $('#city2').val(data.city2);

}

function apply_city(elem) {

    let parent = $(elem).parent('.dropdown_list');
    let edit = $(parent).prev('.dropdown_edit');
    let txt = $(elem).find('span[data-text]')[0];
    $(edit).val(txt.innerText);
    $(parent).addClass('dropdown_hide');
    txtinput_changed(edit);
}
$(document).ready(function () {
    init_vcl();
    //  init();

    /*
    
        $('#lang').on('click', 'img', function () {
            lang = $(this).data('langid');
            send_data({
                'city1': $('#city1').val(),
                'city2': $('#city2').val(),
                'lang': lang,
                sender: 20
            });
        });
    */


    // $('#city1').trigger('focus');
    // $('#city1').focus();
    // txtinput_changed($('#city1'));
    // $('#city1').focus();
});
