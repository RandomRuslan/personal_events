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

        this.signInButton.click(function () { this.authRequest('/signin') }.bind(this));
        this.signUpButton.click(function () { this.authRequest('/signup') }.bind(this));
        this.signOutButton.click(this.signOut.bind(this));
        return this;
    },

    authRequest: function(method) {
        let data = this.getAuthData();
        if (data) {
            $.post(method, data, this.afterAuth.bind(this));
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
            this.authBlock.show();
            this.signOutButton.hide();
            this.authMessage.text(responseData.text);
        }.bind(this));
    }
}

let events = {
    authBlock: null,

    eventsWrapper: null,
    newEventOverlay: null,
    eventCardTemplate: null,
    
    init: function (authBlock) {
        this.authBlock = authBlock;
        this.eventsWrapper = $('#events_wrapper');
        this.newEventOverlay = $('#new_event_overlay', this.eventsWrapper);
        this.eventCardTemplate = $('.event-card', this.eventsWrapper).remove();

        this.addButton = $('#add_event', this.eventsWrapper);
        this.addButton.click(this.addEvent.bind(this));
    },

    addEvent: function () {
        console.log('add button', this.newEventOverlay.is(':visible'));
        if (this.newEventOverlay.is(':visible')) {
            this.newEventOverlay.hide();
        } else {
            this.newEventOverlay.show();
        }
    }
}

$(document).ready(function () {
    let authBlock = auth.init();
    events.init(authBlock);
})