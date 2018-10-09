function ajax(url, data, method, extra, callback) {
    var xmlhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");

    extra = typeof extra !== 'undefined' ? extra : null;

    xmlhttp.open(method, url, true);
    xmlhttp.setRequestHeader('Content-Type', 'application/json');
    xmlhttp.setRequestHeader('X-CSRFToken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
    xmlhttp.send(JSON.stringify(data));

    xmlhttp.onload = function (e) {
        try {
            var data = JSON.parse(e.currentTarget.response);
        } catch (e) {
            var data = {};
        }
        if (callback) {
            callback(data, extra);
        }
    };

}
