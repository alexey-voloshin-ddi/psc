(function () {
    var archive_buttons = document.getElementsByClassName('archive');
    var delete_buttons = document.getElementsByClassName('delete');

    function archivate (element) {
        var id = element.getAttribute('data-id');
        var url = "/api/v1/notifications/" + id + "/archivate/";
        ajax(url, {}, 'POST', element, function (data, extra) {
            var notification_row = document.getElementById('notification-row-' + id);
            notification_row.classList.add('notification-archived');
            notification_row.classList.remove('notification-new');
            document.getElementById('notification-status-' + id).innerText = data.status_text;
            extra.parentNode.removeChild(extra);
        });
        return false;
    }

    for (var i = 0; i < archive_buttons.length; i++) {
        archive_buttons[i].onclick = function () {
            archivate(this);
        }
    }

    for (var i = 0; i < delete_buttons.length; i++) {
        delete_buttons[i].onclick = function () {
            var id = this.getAttribute('data-id');
            var url = "/api/v1/notifications/" + id + "/";
            ajax(url, {}, 'DELETE', this, function (data, extra) {
                extra.parentNode.parentNode.parentNode.removeChild(extra.parentNode.parentNode);
            });
        }
    }


    ajax('/api/v1/notifications/make_read/', {}, "POST", null);

})();
