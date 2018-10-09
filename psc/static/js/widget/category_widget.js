function ajax(url, data, method, extra, callback) {
    var xmlhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
    var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    extra = typeof extra !== 'undefined' ? extra : null;
    xmlhttp.open(method, url, true);

    xmlhttp.send(data);

    xmlhttp.onload = function (e) {
        var data = JSON.parse(e.currentTarget.response);
        if (callback) {
            callback(data, extra);
        }
    };

}

(function() {
    var select_count = 0;
    var containers_count = 0;
    var category_data = JSON.parse(document.getElementById('category-input').value);

    function remove_child (element) {
        var child_element = document.getElementById(element.getAttribute('data-child-select-id'));
        if (child_element) {
            element.parentNode.removeChild(child_element);
            remove_child(child_element);
        }
    }

    function set_data(id, level) {
        category_data['level-' + level] = id;
        document.getElementById('category-input').value = JSON.stringify(category_data);
    }



    function select_change (element) {
        var category_container = element.parentNode;
        var url = '/api/v1/categories/' + element.value + '/children/';

        var children = element.parentNode.childNodes;
        var to_remove = [];
        for (var i = 0; i < children.length; i ++) {
            if (children[i].tagName == 'SPAN' || children[i].tagName == 'INPUT' ) {
                to_remove.push(children[i]);
            }
        }

        for (var i = 0; i < to_remove.length; i++) {
            element.parentNode.removeChild(to_remove[i]);
        }

        ajax(url, {}, 'GET', null, function (data, extra) {
            var child_select = document.getElementById(element.getAttribute('data-child-select-id'));
            if (child_select) {
                if (data.length) {
                    child_select.innerHTML = "";
                    var option_none = document.createElement('option');
                    option_none.innerHTML = '-----';
                    child_select.appendChild(option_none);
                    for (var i = 0; i < data.length; i++) {
                        var option = document.createElement('option');
                        option.setAttribute('value', data[i].id);
                        option.innerHTML = data[i].name;
                        child_select.appendChild(option);
                    }
                    remove_child(child_select);
                } else {
                    remove_child(child_select);
                    child_select.parentNode.removeChild(child_select);
                }
            } else {
                if (data.length) {
                    var select = document.createElement('select');
                    var option_none = document.createElement('option');
                    var select_id = 'select-' + containers_count + '-' + select_count;
                    option_none.innerHTML = '-----';
                    select.setAttribute('id', select_id);
                    element.setAttribute('data-child-select-id', select_id);
                    select.appendChild(option_none);

                    for (var i = 0; i < data.length; i++) {
                        var option = document.createElement('option');
                        option.setAttribute('value', data[i].id);
                        option.innerHTML = data[i].name;
                        select.appendChild(option);
                    }
                    select.addEventListener('change', function () {
                        select_change(this);
                    });
                    category_container.appendChild(select);
                    select_count ++;
                }
            }
            var level = element.parentNode.getAttribute('data-level');
            set_data(element.value, level);
        });
    }

    if (category_data['level-0']) {
        for (var i = 0;;i++) {
            document.getElementById('category').innerHTML = "";
            if (!category_data['level-' + i]) {
                containers_count = i;
                break;
            }
            var url = "/api/v1/categories/" + category_data['level-' + i] + "/list_tree/";
            ajax(url, {}, "GET", i, function (data, extra) {
                var container = document.createElement('div');
                container.setAttribute('id', 'category-container-' + extra);
                container.setAttribute('data-level', extra);
                for (var i = 0; i < data.length; i++) {
                    var select = document.createElement('select');
                    select.setAttribute('id', 'select-' + extra + '-' + i);
                    select.setAttribute('data-child-select-id', 'select-' + extra + '-' + (i + 1));
                    select.addEventListener('change', function () {
                        select_change(this);
                    });
                    for (var j = 0; j < data[i].length; j++) {
                        var option = document.createElement('option');
                        option.setAttribute('value', data[i][j].id);

                        try {
                            if (data[i][j].id == data[i + 1][0].parent) {
                                option.setAttribute('selected', 'selected');
                            }
                        } catch (e) {}

                        if (category_data['level-' + extra] == data[i][j].id) {
                            option.setAttribute('selected', 'selected');
                        }

                        option.innerHTML = data[i][j].name;

                        select.appendChild(option);
                    }
                    container.appendChild(select);
                    if (i == data.length - 1) {
                        var url = '/api/v1/categories/' + select.value + '/children/';
                        var extra_ajax_data = {
                            containers_count: extra,
                            select_count: i + 1,
                            element: select,
                            category_container: container
                        };
                        ajax(url, {}, 'GET', extra_ajax_data, function (data, extra) {
                            if (data.length) {
                                var select = document.createElement('select');
                                var option_none = document.createElement('option');
                                var select_id = 'select-' + extra.containers_count + '-' + extra.select_count;
                                option_none.innerHTML = '-----';
                                select.setAttribute('id', select_id);
                                extra.element.setAttribute('data-child-select-id', select_id);
                                select.appendChild(option_none);

                                for (var i = 0; i < data.length; i++) {
                                    var option = document.createElement('option');
                                    option.setAttribute('value', data[i].id);
                                    option.innerHTML = data[i].name;
                                    select.appendChild(option);
                                }
                                select.addEventListener('change', function () {
                                    select_change(this);
                                });
                                extra.category_container.appendChild(select);
                                select_count ++;
                            }
                        });
                    }
                }

                document.getElementById('category').appendChild(container);
            });
        }
    }

    function suggest_category(element) {
        var input = document.createElement('input');
        var label = document.createElement('span');
        label.innerHTML = 'Suggest Category:';
        element.parentNode.appendChild(label);
        element.parentNode.appendChild(input);
        remove_child(element);
    }

    try {
        document.getElementById('base-category-select').addEventListener('change', function () {
            var selected_option_text = this.options[this.selectedIndex].innerText;
            if (selected_option_text.toLowerCase() != 'other') {
                select_change(this);
            } else {
                suggest_category(this);
            }
        });
    } catch (e) {}


    document.getElementById('add-more').onclick = function () {
        ajax('/api/v1/categories/top/', {}, 'GET', null, function (data, extra) {
            containers_count ++;
            var container = document.createElement('div');
            var select = document.createElement('select');
            container.setAttribute('id', 'category-container-' + containers_count);
            container.setAttribute('data-level', containers_count);

            var option_none = document.createElement('option');
            option_none.innerHTML = '-----';
            select.appendChild(option_none);
            select.addEventListener('change', function () {
                select_change(this);
            });
            for (var i = 0; i < data.length; i++) {
                var option = document.createElement('option');
                option.setAttribute('value', data[i].id);
                option.innerHTML = data[i].name;
                select.appendChild(option);
            }

            container.appendChild(select);

            document.getElementById('category').appendChild(container);

        });
        return false;
    }
})();
