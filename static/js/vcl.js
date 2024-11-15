

function apply_city(elem) {

    let dropdown_list = $(elem).parent('.dropdown_list');
    let input = $(dropdown_list).prev('input');
    let txt = $(elem).find('.city')[0];
    $(input).val(txt.innerText);

    let wrapper = $(input).parents('.wrapper');
    let field_name = $(wrapper).attr('id');
    save_storage(field_name, txt.innerText);

    $(dropdown_list).addClass('hide');
    city_input_changed(input);
}
function city_input_changed(input) {

    let data = collect_fields(['city1', 'city2']);
    data['lang'] = load_storage('lang', 0)

    data['sender'] = $(input).parents('.wrapper').attr('id');
    send_data(data);
}
function city_input_keydown(input, event) {
    let dropdown_list = $(input).next('.dropdown_list')[0];
    // exit, if dropdown list not visible
    let hided = $(dropdown_list).hasClass('hide');
    if (hided)
        return;

    let handled = true;

    let items = $(dropdown_list).children();
    // get current selection 
    let sel_index = $(dropdown_list).find('.selected').index();
    let items_count = items.length;

    switch (event.keyCode) {
        case 27:
            // Esc
            $(dropdown_list).addClass('hide');
            $(el).blur();
            break;
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
            $(input).blur();
            apply_city(selected);

            break;
        default:
            handled = false;
    }
    if (handled) {

        $(items).removeClass('selected');
        let selected = items.eq(sel_index);
        $(selected).addClass('selected');

        event.preventDefault();
    }
}
function check_edit_empty(wrapper) {
    // check value for label
    let input = $(wrapper).find('.inp');
    let value = input.val();
    let label = $(wrapper).find('label');
    if (value.length > 0) {
        $(wrapper).removeClass('empty_input');
    } else
        $(wrapper).addClass('empty_input');
}
function init_vcl() {
    //
    // DROPDOWN handlers
    // 
    $('[data-type="dropdown"] input').on('input', function () {
        city_input_changed(this);
    }).on('focus', function () {
        // city_input_changed(this);
    }).on('keydown', function (e) {
        city_input_keydown(this, e);
    });

    $('.dropdown_list').on("mouseover", 'div', function () {
        // console.log( $( this ).text() );
        $(this).parent().children().removeClass('selected');
        $(this).addClass('selected');
    }).on("click", 'div', function () {
        apply_city(this);

    });

    //
    // DROPDOWN off click
    // 
    $('body,html').click(function (event) {
        // look if we move out from somekind dropdown
        // находим родительскую ближайшую область dropdown_cont
        let current_dd = $(event.target).closest('.dropdown');
        if (current_dd.length > 0)
            current_dd = current_dd[0]

        // пробегаем по всем дропдаунам на странице
        $('.dropdown').each(function () {
            // let parent = $(this).parent()[0];
            if (this == current_dd) {// console.log('in edit');
                // event.preventDefault();
                // return false;
            } else {
                $(this).children('.dropdown_list').addClass('hide');
                // console.log(this + 'hided');
            }

        });
    });

    //
    // load stored for ALL inputs
    //
    $('.wrapper').each(function () {
        let field_name = $(this).attr('id');
        let value = load_storage(field_name, '');
        let input = $(this).find('.inp');

        input.val(value);
        check_edit_empty(this);
    });
    $('.wrapper .inp').on('focus', function () {
        let wrapper = $(this).parents('.wrapper');
        check_edit_empty(wrapper);
        //let label = $(parent).find('label');        label.removeClass('hs');
    }).on('input', function () {
        // save modified input for SIMPLE  
        let wrapper = $(this).parents('.wrapper');
        let field_name = $(wrapper).attr('id');
        let value = $(this).val();
        save_storage(field_name, value);

        check_edit_empty(wrapper);
    });
    $('[data-type="date"] input').on('focus', function () {/*console.log('date focus');*/
    }).on('blur', function () {/*    console.log('date blur');*/
    });

    $('[data-type] .err').addClass('hide');
    $('[data-type] input').on('focus', function () {
        $('[data-type] .err').addClass('hide');
    });
}
