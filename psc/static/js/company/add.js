(function () {
    //document.getElementById('add-more-offices').onclick = function () {
    //    var forms_count = parseInt(document.getElementById('id_company-TOTAL_FORMS').value) + 1;
    //    document.getElementById('id_company-TOTAL_FORMS').value = forms_count;
    //
    //    var clone = document.getElementById('offices').getElementsByTagName('table')[0].cloneNode(true);
    //
    //    var inputs = clone.getElementsByTagName('input');
    //    var selects = clone.getElementsByTagName('select');
    //    var text_areas = clone.getElementsByTagName('textarea');
    //
    //    var controls = [];
    //    controls.push.apply(controls, inputs);
    //    controls.push.apply(controls, selects);
    //    controls.push.apply(controls, text_areas);
    //    console.log(controls);
    //
    //    for(var i=0; i<controls.length; i++) {
    //        var splited_name = controls[i].name.split('-');
    //        splited_name[1] = forms_count - 1;
    //        var new_name = splited_name.join('-');
    //        controls[i].setAttribute('name', new_name);
    //        controls[i].setAttribute('id', 'id_' + new_name);
    //    }
    //
    //    document.getElementById('offices').appendChild(clone);
    //
    //    return false;
    //}
})();
