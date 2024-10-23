function init_vcl()
{
//<input type="text" data-init="{'handler':'parse_data','id':'city1'}"></div>

$(''



}

/*
// text input handlers
$('.dropdown_edit').on('input', function () {
    txtinput_changed(this);
}).on('focus', function () {
    txtinput_changed(this);
}).on('blur', function () {// this dont work!!  $(this).next('.dropdown_list').addClass("dropdown_hide");

}).on('keydown', function (e) {
    let list = $(this).next('.dropdown_list')[0];
    // exit, if dropdown list not visible
    let hided = $(list).hasClass('dropdown_hide');
    if (hided)
        return;

    let handled = true;

    let items = $(list).children();
    // get current selection 
    let sel_index = $(list).find('.selected').index();
    let items_count = items.length;

    switch (event.keyCode) {
        case 27: // Esc
            $(list).addClass('dropdown_hide');
            $(this).blur();
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
            $(this).blur();
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
    ;

});

$('.dropdown_list').on("mouseover", 'div', function () {
    // console.log( $( this ).text() );
    $(this).parent().children().removeClass('selected');
    $(this).addClass('selected');
}).on("click", 'div', function () {
    apply_city(this);

});



$(document).click(function (event) {
    // look if we move out from somekind dropdown
    current_dd = $(event.target).closest('.dropdown_cont');
    if (current_dd.length > 0)
        current_dd = current_dd[0]
    $('div.dropdown_cont').each(function () {
        if (this == current_dd) {
            // console.log('in edit');
            // event.preventDefault();
            // return false;
        } else {
            $(this).children('.dropdown_list').addClass('dropdown_hide');
            // console.log(this + 'hided');
        }

    });
});

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
*/


