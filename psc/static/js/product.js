(function() {

    document.getElementById('add-more-documents').onclick = function (e) {
        var forms_count = parseInt(document.getElementById('id_documentation_set-TOTAL_FORMS').value) + 1;
        document.getElementById('id_documentation_set-TOTAL_FORMS').value = forms_count;

        var clone = document.getElementById('documents').getElementsByTagName('table')[0].cloneNode(true);

        var inputs = clone.getElementsByTagName('input');

        for(var i=0; i<inputs.length; i++) {
            if (inputs[i].name == 'documentation_set-0-name') {
                inputs[i].setAttribute('id', 'id_documentation_set-'+(forms_count - 1)+'-name');
                inputs[i].setAttribute('name', 'documentation_set-'+(forms_count - 1)+'-name');
            } else {
                inputs[i].setAttribute('id', "id_documentation_set-"+(forms_count - 1)+"-path");
                inputs[i].setAttribute('name', "documentation_set-"+(forms_count - 1)+"-path");
            }
        }

        document.getElementById('documents').appendChild(clone);

        return false;
    };

    document.getElementById('add-more-videos').onclick = function (e) {
        var forms_count = parseInt(document.getElementById('id_video_set-TOTAL_FORMS').value) + 1;
        document.getElementById('id_video_set-TOTAL_FORMS').value = forms_count;

        var clone = document.getElementById('videos').getElementsByTagName('table')[0].cloneNode(true);

        var inputs = clone.getElementsByTagName('input');

        for(var i=0; i<inputs.length; i++) {

            if (inputs[i].name == 'video_set-0-name') {
                inputs[i].setAttribute('id', 'id_video_set-'+(forms_count - 1)+'-name');
                inputs[i].setAttribute('name', 'video_set-'+(forms_count - 1)+'-name');
            } else {
                var input_name = String(inputs[i].name);
                var end_str = '-user_path';

                if (input_name.endsWith('-id')){
                    end_str = '-id';
                }
                else if (input_name.endsWith('-product')){
                    end_str = '-product';
                }
                inputs[i].setAttribute('id', "id_video_set-"+(forms_count - 1)+ end_str);
                inputs[i].setAttribute('name', "video_set-"+(forms_count - 1)+ end_str);
            }
        }

        document.getElementById('videos').appendChild(clone);

        return false;
    }


})();
