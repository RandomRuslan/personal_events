let auth = {
    authBlock: null,
    signInButton: null,
    signUpButton: null,
    authMessage: null,

    signOutButton: null,

    eventCardTemplate: null,

    init: function () {
        this.authBlock = $('#auth');
        this.signInButton = $('#sign_in', this.authBlock);
        this.signUpButton = $('#sign_up', this.authBlock);
        this.authMessage = $('#auth_message', this.authBlock);

        this.signOutButton = $('#sign_out');

        this.eventCardTemplate = $('.event-card').remove();

        this.signInButton.click(this.signIn.bind(this));
        this.signUpButton.click(this.signUp.bind(this));
        this.signOutButton.click(this.signOut.bind(this));
    },

    signIn: function() {
        let data = this.getAuthData();
        if (data) {
            $.post('/signin', data, function (responseData) {
                this.afterAuth(responseData);
            }.bind(this))
        }
    },

    signUp: function() {
        let data = this.getAuthData();
        if (data) {
            $.post('/signup', data, function (responseData) {
                this.afterAuth(responseData);
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
    },

    afterAuth: function(responseData) {
        console.log(responseData);
        this.authMessage.toggleClass('error', responseData.error);
        if (responseData.error) {
            this.authMessage.text(responseData.text);
        } else {
            this.authBlock.hide();
            this.signOutButton.show();
        }
    },

    signOut: function () {
        $.post('/signout', {}, function (responseData) {
            console.log(responseData);
            this.authBlock.show()
            this.signOutButton.hide()
            this.authMessage.text(responseData.text);
        }.bind(this))

    }
}

$(document).ready(function () {
    auth.init();
})