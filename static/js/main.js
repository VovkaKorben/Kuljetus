let myStorage = undefined;

function save_storage(key, value) {
    if (myStorage === undefined)
        myStorage = window.localStorage;
    myStorage.setItem(key, value);
}
function load_storage(key, def) {
    if (myStorage === undefined)
        myStorage = window.localStorage;
    p = myStorage.getItem(key);
    if (p === null)
        p = def;
    return p;
}

function parse_answer(result) {
    if ('data'in result) {
        for (k in result.data) {
            // console.log('data parse_answer:', k, '', result.data[k]);
            save_storage(k, result.data[k]);
        }

    }

    if ('dom'in result) {

        jQuery.each(result.dom, function(index, item) {
            // do something with `item` (or `this` is also `item` if you like)
            elem = $(item.selector);
            if (elem) {
                if ('html'in item)
                    $(elem).html(item.html);
                if ('css_add'in item)
                    jQuery.each(item.css_add, function(index, item) {
                        $(elem).addClass(item);
                    });
                if ('css_remove'in item)
                    jQuery.each(item.css_remove, function(index, item) {
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
        'city1': load_storage('city1', 'ccc'),
        'city2': load_storage('city2', 'ddd'),
    }
    send_data( data);

}

$(document).ready(function() {

    init();
    $('#mista,#mihin').on('input', function() {
        alert('123');
    });
    $('#lang img').on('click', function() {
        lang_id = $(this).data('langid');
        // alert('lang_id: ' + lang_id);
        send_data({'lang': lang_id});
    });

});
