let auth = {
    authBlock: null,
    signInButton: null,
    signUpButton: null,
    authMessage: null,

    eventCardTemplate: null,

    init: function () {
        this.authBlock = $('#auth');
        this.signInButton = $('#sign_in', this.authBlock);
        this.signUpButton = $('#sign_up', this.authBlock);
        this.authMessage = $('#auth_message', this.authBlock);

        this.eventCardTemplate = $('.event-card').remove();

        this.signInButton.click(this.signIn.bind(this));
        this.signUpButton.click(this.signUp.bind(this));
    },


    signIn: function() {
        let data = this.getAuthData()
        console.log('SIGN IN: ', data);

        if (data) {
            $.post('/signin', data, function (responseData) {
                this.authMessage.text(responseData.text);
                this.authMessage.toggleClass('error', responseData.error);
                this.authMessage.show();
                console.log(responseData);
            }.bind(this))
        }
    },

    signUp: function() {
        let data = this.getAuthData()
        console.log('SIGN UP: ', data);

        if (data) {
            $.post('/signup', data, function (responseData) {
                this.authMessage.text(responseData.text);
                this.authMessage.toggleClass('error', responseData.error);
                this.authMessage.show();
                console.log(responseData);
            }.bind(this))
        }
    },

    getAuthData: function () {
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

        return !emptyError ? data : null;
    }
}

$(document).ready(function () {
    auth.init();
})