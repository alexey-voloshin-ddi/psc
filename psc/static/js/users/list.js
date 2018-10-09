(function () {

    var cancel_invite_buttons = document.getElementsByClassName('cancel-invite');
    var confirm_user_buttons = document.getElementsByClassName('confirm-user');
    var make_owner_buttons = document.getElementsByClassName('make-owner');
    var terminate_user_buttons = document.getElementsByClassName('terminate-user');
    var resend_invite_buttons = document.getElementsByClassName('resend-invite');

    for (var i = 0; i < resend_invite_buttons.length; i++) {
        resend_invite_buttons[i].onclick = function () {
            var id = this.getAttribute('data-id');
            var url = '/api/v1/invitations/' + id + '/resend/';
            this.setAttribute('disabled', 'disabled');
            this.innerText = 'Resending in progress';
            ajax(url, {}, 'POST', this, function (data, extra) {
                var children = extra.parentNode.childNodes;
                for (var i=0; i<children.length; i++) {
                    try {
                        children[i].setAttribute('data-id', data.id);
                    } catch (e) {}
                }
                extra.removeAttribute('disabled');
                extra.innerText = 'Resend';
            });
        }
    }

    for (var i = 0; i < cancel_invite_buttons.length; i++) {
        cancel_invite_buttons[i].onclick = function () {
            var id = this.getAttribute('data-id');
            var url = '/api/v1/invitations/' + id + '/';
            ajax(url, {}, 'DELETE', this, function (data, extra) {
                extra.parentNode.parentNode.parentNode.removeChild(extra.parentNode.parentNode);
            });
        }
    }

    for (var i = 0; i < confirm_user_buttons.length; i++) {
        confirm_user_buttons[i].onclick = function () {
            var id = this.getAttribute('data-id');
            var url = '/api/v1/users/' + id + '/confirm/';
            ajax(url, {}, 'POST', this, function (data, extra) {
                location.reload();
            });
        }
    }

    for (var i = 0; i < make_owner_buttons.length; i++) {
        make_owner_buttons[i].onclick = function () {
            var id = this.getAttribute('data-id');
            var url = '/api/v1/users/' + id + '/make_owner/';
            ajax(url, {}, 'POST', this, function (data, extra) {
                location.reload();
            });
        }
    }

    for (var i = 0; i < terminate_user_buttons.length; i++) {
        terminate_user_buttons[i].onclick = function () {
            var id = this.getAttribute('data-id');
            var url = '/api/v1/users/' + id + '/';
            ajax(url, {}, 'DELETE', this, function (data, extra) {
                location.reload();
            });
        }
    }

})();
