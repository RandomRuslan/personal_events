let auth = {
    authBlock: null,

    init: function () {
        this.authBlock = $('#auth');
        this.authButton = $('#auth_button', this.authBlock);
        this.authMessage = $('#auth_message', this.authBlock);

        this.authButton.click(this.onAuthButtonHandler.bind(this));
    },

    onAuthButtonHandler: function() {
        let emptyError = false;
        let data = {}

        $('input', this.authBlock).each(function() {
            let el = $(this);
            if (!el.val()) {
                el.addClass('error');
                emptyError = true;
            } else {
                el.removeClass('error');
                data[el.attr('name')] = el.val()
            }
        })

        if (!emptyError) {
            console.log('send data', data);
            $.post('/', data, function (responseData) {
                this.authMessage.text(responseData.text);
                this.authMessage.toggleClass('error', responseData.error);
                this.authMessage.show();
                console.log(responseData);
            }.bind(this))
        }

    }
}

$(document).ready(function () {
    auth.init();
})