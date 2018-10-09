(function () {

    var delete_buttons = document.getElementsByClassName('delete');

    for (var i = 0; i < delete_buttons.length; i ++) {
        delete_buttons[i].onclick = function () {
            var id = this.getAttribute('data-id');
            var url = '/api/v1/products/' + id + '/';
            ajax(url, {}, "DELETE", this, function (data, extra) {
                extra.parentNode.parentNode.parentNode.removeChild(extra.parentNode.parentNode);
            });
        }
    }

})();
