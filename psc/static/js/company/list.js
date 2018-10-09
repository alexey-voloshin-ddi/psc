
(function () {
    var delete_buttons = document.getElementsByClassName('delete');

    for (var i=0; i<delete_buttons.length; i++) {
        delete_buttons[i].onclick = function () {
            var company_id = this.getAttribute('data-id');
            var url = '/api/v1/company/' + company_id + '/';
            var row = this.parentNode.parentNode;

            ajax(url, {}, "DELETE", null, function (data, extra) {
                row.parentNode.removeChild(row);
            });
        }
    }
})();
