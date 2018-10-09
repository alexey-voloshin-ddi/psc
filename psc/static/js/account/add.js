(function () {
    var add_more_ci = document.getElementById('add-more-contact-information');
    var delete_account = document.getElementById('delete-account');
    var restore_account = document.getElementById('restore-account');

    if (add_more_ci) {
        add_more_ci.onclick = function () {
            var forms_count = parseInt(document.getElementById('id_contactinformation_set-TOTAL_FORMS').value) + 1;
            document.getElementById('id_contactinformation_set-TOTAL_FORMS').value = forms_count;

            var clone = document.getElementById('offices').getElementsByTagName('table')[0].cloneNode(true);

            var inputs = clone.getElementsByTagName('input');
            var selects = clone.getElementsByTagName('select');
            var text_areas = clone.getElementsByTagName('textarea');

            var controls = [];
            controls.push.apply(controls, inputs);
            controls.push.apply(controls, selects);
            controls.push.apply(controls, text_areas);

            for(var i=0; i<controls.length; i++) {
                controls[i].value = null;
                var splited_name = controls[i].name.split('-');
                splited_name[1] = forms_count - 1;
                var new_name = splited_name.join('-');
                controls[i].setAttribute('name', new_name);
                controls[i].setAttribute('id', 'id_' + new_name);
            }

            document.getElementById('offices').appendChild(clone);

            return false;
        };
    }

    if (delete_account) {
        delete_account.onclick = function () {
            ajax('/api/v1/accounts/deactivate_account/', {}, 'POST', null, function (data, extra) {
                location.reload();
            });
        }
    }

    if (restore_account) {
        restore_account.onclick = function () {
            ajax('/api/v1/accounts/restore_account/', {}, 'POST', null, function (data, extra) {
                location.reload();
            });
        }
    }

})();
