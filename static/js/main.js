const LANG_KEY = 'lang_id'

function parse_answer(result) {
    if ('storage'in result) {
        for (k in result.storage) {
            save_storage(k, result.storage[k]);
        }
    }

    if ('dom'in result) {
        jQuery.each(result.dom, function(index, item) {
            // do something with `item` (or `this` is also `item` if you like)
            let elem = $(item.selector);

            // console.log(JSON.stringify(item, null, 2));
            if (elem.length > 0) {

                if ('html'in item)
                    $(elem).html(item.html);

                if ('css_add'in item)
                    jQuery.each(item.css_add, function(i, v) {
                        $(elem).addClass(v);
                    });
                if ('css_remove'in item)
                    jQuery.each(item.css_remove, function(i, v) {
                        $(elem).removeClass(v);
                    });
                if ('attr_set'in item)
                    jQuery.each(item.attr_set, function(i, v) {
                        $(elem).attr(v.attr, v.value);
                    });

            } else
                console.log(`[parse_answer] selector '${item.selector}' not found.`);

        });
    }
}
function request_translation(full) {

   //     if (full)        field_list = [];    else
        field_list = ['city1', 'city2'];
    data = collect_fields(field_list);
    data['full'] = full;
        data[LANG_KEY] =  load_storage(LANG_KEY, 0);
    data['sender'] = 'LANG';
    send_data(data);
}
function collect_fields(fields) {
    if (fields.length == 0)
        // for empty input get all fields

        $('[data-type]').each(function() {
            fieldname = $(this).attr('id');
            fields.push(fieldname);
        });

    let collect = {};
    $.each(fields, function(i, v) {
        let fieldval = $(`#${v}`).find('.inp').val();
        collect[v] = fieldval;
    });
    return collect;
}

function send_data(data) {

    fetch('/parse_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json()).then(result => {
        parse_answer(result);
    }
    ).catch(error => {
        console.log(`Error: ${error}`);
    }
    );
}

/*
function change_lang(lang_id) {
    send_data({
        'lang': lang_id,
        sender: 'lang'
    });

}
*/
$(document).ready(function() {
    // setup dropdown etc
    init_vcl();

    // language handler
    $('#lang').on('click', 'img', function() {
        let lang_id = $(this).data('langid');
        save_storage(LANG_KEY, lang_id);
        request_translation(1);
    });
    // init page with language request
    request_translation(1);
    // change_lang(load_storage('lang', 0));

    // hide errors
    // $('.err').addClass('hide');

    // send application
    $('#sendapp').on('click', function() {
        data = collect_fields([]);
        // empty for all
        data['sender'] = 'sendapp';
        data['lang'] = load_storage('lang', 0);
        send_data(data);
    });

    // $('#sendapp').trigger('click');

    // city_input_changed($('#city2_input'));    $('#city2_input').focus();
});
