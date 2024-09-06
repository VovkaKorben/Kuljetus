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
        'city1': load_storage('city1', ''),
        'city2': load_storage('city2', ''),
        'sender': 0
    }
    send_data(data);
    $('#city1').val(data.city1);
    $('#city2').val(data.city2);

}
function txtinput_changed(edit) {
    let sender = 10 + parseInt($(edit).data('id'));
    let data = {
        'city1': $('#city1').val(),
        'city2': $('#city2').val(),
        'lang': load_storage('lang', 0),
        sender: sender
    }
    send_data(data);
}
function apply_city(elem) {

    let parent = $(elem).parent('.dropdown_list');
    let edit = $(parent).prev('.dropdown_edit');
    let txt = $(elem).find('span[data-text]')[0];
    $(edit).val(txt.innerText);
    $(parent).addClass('dropdown_hide');
    txtinput_changed(edit);
}
$(document).ready(function() {

    init();

    // text input handlers
    $('.dropdown_edit').on('input', function() {
        txtinput_changed(this);
    }).on('focus', function() {
        txtinput_changed(this);
    }).on('blur', function() {// this dont work!!  $(this).next('.dropdown_list').addClass("dropdown_hide");

    }).on('keydown', function(e) {
        let list = $(this).next('.dropdown_list');
        // exit, if dropdown list not visible
        if (!$(list).hasClass('dropdown_hide'))
            return;

        let handled = true;

        let items = list.children();
        // get current selection 
        let sel_index = list.find('.selected').index();
        let items_count = items.length;

        switch (event.keyCode) {

        case 38:
            // arrow up
            sel_index--;
            if (sel_index < 0)
                sel_index = items_count - 1;
            break;
        case 40:
            // arrow down
            sel_index++;
            if (sel_index >= items_count)
                sel_index = 0;
            break;

        case 13:
            // enter
            // if (sel_index >= 0 && sel_index < items_count) {
            let selected = items.eq(sel_index);
            apply_city(selected);

            break;
        default:
            handled = false;
        }
        if (handled) {

            items.removeClass('selected');
            let selected = items.eq(sel_index);
            selected.addClass('selected');

            event.preventDefault();
        }
        ;

    });

    $('.dropdown_list').on("mouseover", 'div', function() {
        // console.log( $( this ).text() );
        $(this).parent().children().removeClass('selected');
        $(this).addClass('selected');
    }).on("click", 'div', function() {
        apply_city(this);

    });

    $('#lang').on('click', 'img', function() {
        lang = $(this).data('langid');
        send_data({
            'city1': $('#city1').val(),
            'city2': $('#city2').val(),
            'lang': lang,
            sender: 20
        });
    });

    $(document).click(function(event) {
        // look if we move out from somekind dropdown
        current_dd = $(event.target).closest('.dropdown_cont');
        if (current_dd.length>0)
            current_dd = current_dd[0]
        $('div.dropdown_cont').each(function() {
            if (this == current_dd) {
                console.log('in edit');
                 // event.preventDefault();
                // return false;
            } else {
                $(this).children('.dropdown_list').addClass('dropdown_hide');
                console.log(this + 'hided');
            }

        });

        // console.log(ddc);
        /*
        

        if ($(event.target).closest('.dropdown_cont').length > 0) {
            // Элемент находится внутри .dropdown_cont или является им
            console.log('Элемент находится в dropdown_cont или его дочерних');
        } else {
            // Элемент находится вне .dropdown_cont
            console.log('Элемент вне dropdown_cont');
        }
            */
    });
    // $('#city1').trigger('focus');
    // $('#city1').focus();
    // txtinput_changed($('#city1'));
    // $('#city1').focus();
});
