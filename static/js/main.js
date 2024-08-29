function delete_storage(key) {
    if (myStorage === undefined)
        myStorage = window.localStorage;
    p = myStorage.getItem(key);
    result = p !== null;
    if (result)
        myStorage.removeItem(key);
    return result;

}
function save_storage(key, value) {
    if (myStorage === undefined)
        myStorage = window.localStorage;
    p = myStorage.getItem(storage_key);
    if (p === null)
        p = {};
    else
        p = jQuery.parseJSON(p);
    p[key] = value;
    myStorage.setItem(storage_key, JSON.stringify(p));
}
function load_storage(key, def) {
    if (myStorage === undefined)
        myStorage = window.localStorage;
    p = myStorage.getItem(storage_key);
    if (p === null)
        p = {};
    else
        p = jQuery.parseJSON(p);
    if (key in p)
        return p[key];
    else
        return def;
}

$(document).ready(function () {
    // alert('JS work');
    // return;
    // token = load_storage(token_key, "");
    
    $('#mista,#mihin').on('input', function () {
        alert('123');
    });

 

});
