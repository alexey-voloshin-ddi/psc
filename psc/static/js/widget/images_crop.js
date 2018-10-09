var cropper = null;
var image_file = null;
var image_data = [];
var to_delete = [];
var selected_img_id = null;
var xmlhttp = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");

function init_cropper (ready_callback) {
    ready_callback = typeof ready_callback !== 'undefined' ? ready_callback : null;
    return new Cropper(document.getElementById('image_to_crop'), {
        aspectRatio: 1,
        responsive: false,
        preview: '.img-preview',
        zoomable: false,
        ready: ready_callback
    });
}

function show_spinner () {
    document.getElementById('ajax-spinner').classList.remove('hidden');
    document.getElementById('save').setAttribute('disabled', 'disabled');
    document.getElementById('upload-image').setAttribute('disabled', 'disabled');
}

function hide_spinner () {
    document.getElementById('ajax-spinner').classList.add('hidden');
    document.getElementById('save').removeAttribute('disabled');
    document.getElementById('upload-image').removeAttribute('disabled');
}

function show_modal (is_visibility) {
    is_visibility = typeof is_visibility !== 'undefined' ? is_visibility : false;
    if (is_visibility) {
        document.getElementById('modal').classList.add('hidden-visibility');
        document.getElementById('modal-bg').classList.add('hidden-visibility');
    }

    if (cropper) {
        cropper.destroy();
        cropper = null;
    }

    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal-bg').classList.remove('hidden');
    document.getElementById('image_to_crop').src = '';
    document.getElementById('image-format-error').classList.add('hidden');
}

function hide_modal () {
    document.getElementById('modal').classList.add('hidden');
    document.getElementById('modal-bg').classList.add('hidden');
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    xmlhttp.abort();
    document.getElementById('uploaded-image').value = "";
    document.getElementById('modal').classList.remove('hidden-visibility');
    document.getElementById('modal-bg').classList.remove('hidden-visibility');
    hide_spinner();
}

function submitFormAjax(file)
{
    var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;

    xmlhttp.open("POST","/products/upload/image/", true);

    var form_data = new FormData();
    form_data.append("file", file);
    if (is_company) {
        form_data.append('is_company', true);
    }
    form_data.append("csrfmiddlewaretoken", csrf_token);

    xmlhttp.onreadystatechange = function() {

        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var data = JSON.parse(xmlhttp.responseText);
            if (data.error) {
                var error_element = document.getElementById('image-format-error');
                error_element.innerText = data.error;
                error_element.classList.remove('hidden');
                document.getElementById('ajax-spinner').classList.add('hidden');
                document.getElementById('upload-image').removeAttribute('disabled');
            } else {
                document.getElementById('image_to_crop').src = data.url;
                cropper = init_cropper(hide_spinner);
            }

        }
    };

    xmlhttp.send(form_data);
}

function changeimg(str) {
    show_spinner();
    submitFormAjax(image_file);
}


function set_images (image_data, i) {
    if (image_data[i]) {
        document.getElementById('image_to_crop').src = '/media/' + image_data[i].source;
        var tmp_cropper = new Cropper(document.getElementById('image_to_crop'), {
            aspectRatio: 1,
            responsive: false,
            preview: '.img-preview',
            viewMode: 1,
            zoomable: false,
            data: {
                x: image_data[i].x,
                y: image_data[i].y,
                height: image_data[i].height,
                width: image_data[i].width,
                rotate: image_data[i].rotate,
                scaleX: image_data[i].scaleX,
                scaleY: image_data[i].scaleY
            },
            ready: function () {
                var clone = document.getElementById('to-clone').cloneNode(true);
                var image_id = image_data[i].id;

                var image_list =  document.getElementById('cropper-images');
                var image_box = document.getElementById('id_' + input_name);
                var delete_button = document.createElement('div');
                var edit_button = document.createElement('div');

                delete_button.classList.add('img-btn');
                delete_button.classList.add('delete');
                delete_button.innerHTML = 'Del';

                edit_button.classList.add('img-btn');
                edit_button.classList.add('edit');
                edit_button.innerHTML = 'Edit';

                image_list.insertBefore(clone, image_list.childNodes[image_list.childNodes.length - 2]);

                edit_button.onclick = function () {
                    selected_img_id = clone.getAttribute('data-image-id');
                    show_modal();
                };

                delete_button.onclick = function () {
                    var remove_id = clone.getAttribute('data-image-id');
                    var elem = document.getElementById('image-id-' + remove_id);
                    delete_image(elem, remove_id, image_box);
                };

                clone.classList.remove('img-preview');
                clone.classList.remove('lg-preview');
                clone.classList.add('max-size');
                clone.classList.add('image-added');
                clone.setAttribute('data-image-id', image_id);
                clone.appendChild(edit_button);
                clone.appendChild(delete_button);
                clone.setAttribute('id', 'image-id-'+ image_id);

                tmp_cropper.destroy();
                document.getElementById('image_to_crop').src = "";
                set_images(image_data, i+1);
            }
        });
    } else {
        hide_modal();
    }
}

function delete_image (elem, remove_id, image_box) {
    elem.parentNode.removeChild(elem);
    if (image_data.length > 1) {
        for (var i = 0; i < image_data.length; i++) {
            if (image_data[i].id == remove_id) {
                image_data.splice(i, 1);
            }
        }
    } else {
        image_data = [];
    }

    if (is_single) {
        document.getElementById('add').classList.remove('hidden');
    }

    image_box.value = JSON.stringify(image_data);
}

(function() {
    var images_data_input = document.getElementById('id_' + input_name);
    var edit_buttons = document.getElementsByClassName('edit');
    var delete_buttons = document.getElementsByClassName('delete');

    for (var i = 0; i<delete_buttons.length; i++) {
        delete_buttons[i].onclick = function () {
            var elem = this.parentNode;
            var remove_id = elem.getAttribute('data-id');
            elem.parentNode.removeChild(elem);
            to_delete.push(remove_id);
            document.getElementById('id_images_to_delete').value = JSON.stringify(to_delete);
        }
    }

    for (var i = 0; i<edit_buttons.length; i++) {
        edit_buttons[i].onclick = function () {
            selected_img_id = this.parentNode.getAttribute('data-image-id');
            show_modal();
            if (!is_single || is_company) {
                to_delete.push(this.parentNode.getAttribute('data-id'));
                document.getElementById('id_images_to_delete').value = JSON.stringify(to_delete);
            }
        }
    }

    if (images_data_input.value) {
        image_data = JSON.parse(images_data_input.value);
        show_modal(true);
        if (is_single) {
            document.getElementById('add').classList.add('hidden');
        }
        set_images(image_data, 0);
    }
    try {
        document.getElementById('add').onclick = function(e){
            selected_img_id = null;
            show_modal();
        };
    } catch (e) {}

    document.getElementById('modal-bg').onclick = function(e){
        hide_modal();
    };

    document.getElementById('close-modal').onclick = function(e){
        hide_modal();
    };

    document.getElementById('upload-image').onclick = function (e){
        document.getElementById('uploaded-image').click();
    };

    document.getElementById('uploaded-image').addEventListener('change', function () {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        image_file = this.files[0];
        if (!image_file.name.match(/.(jpg|jpeg|png|gif)$/i)) {
            document.getElementById('image-format-error').innerText = "Wrong file format. Allow images only (jpg, jpeg, png, gif)";
            document.getElementById('image-format-error').classList.remove('hidden');
        } else {
            var file_reader = new FileReader;
            file_reader.onloadend = changeimg;
            file_reader.readAsDataURL(image_file);
            document.getElementById('image-format-error').classList.add('hidden');
        }
    });

    document.getElementById('save').onclick = function (e) {
        var clone = document.getElementById('to-clone').cloneNode(true);
        var data = cropper.getData();
        var image_box = document.getElementById('id_' + input_name);
        var image_list =  document.getElementById('cropper-images');

        var delete_button = document.createElement('div');
        var edit_button = document.createElement('div');

        delete_button.classList.add('img-btn');
        delete_button.classList.add('delete');
        delete_button.innerHTML = 'Del';

        edit_button.classList.add('img-btn');
        edit_button.classList.add('edit');
        edit_button.innerHTML = 'Edit';

        if (selected_img_id == null) {

            clone.classList.remove('img-preview');
            clone.classList.remove('lg-preview');
            clone.classList.add('max-size');
            clone.classList.add('image-added');
            clone.setAttribute('data-image-id', image_id);
            clone.appendChild(edit_button);
            clone.appendChild(delete_button);
            clone.setAttribute('id', 'image-id-'+ image_id);

            image_list.insertBefore(clone, image_list.childNodes[image_list.childNodes.length - 2]);

            edit_button.onclick = function () {
                selected_img_id = clone.getAttribute('data-image-id');
                show_modal();
            };

            delete_button.onclick = function () {
                var remove_id = clone.getAttribute('data-image-id');
                var elem = document.getElementById('image-id-' + remove_id);
                delete_image(elem, remove_id, image_box);
            };

            if (is_single) {
                document.getElementById('add').classList.add('hidden');
            }

            data.id = image_id;
            image_id ++;
        } else {
            var edited_elem = document.getElementById('image-id-' + selected_img_id);
            edited_elem.innerHTML = clone.innerHTML;
            edited_elem.appendChild(edit_button);
            edited_elem.appendChild(delete_button);
            edit_button.onclick = function () {
                selected_img_id = edited_elem.getAttribute('data-image-id');
                show_modal();
            };

            delete_button.onclick = function () {
                var remove_id = edited_elem.getAttribute('data-image-id');
                var elem = document.getElementById('image-id-' + remove_id);
                delete_image(elem, remove_id, image_box);
            };

            for(var i=0; i<image_data.length; i++) {
                if (image_data[i].id == selected_img_id) {
                    image_data.splice(i, 1);
                }
            }
            data.id = selected_img_id;
        }

        data.source = image_file.name;

        image_data.push(data);

        image_box.value = JSON.stringify(image_data);

        hide_modal();
    };

})();
