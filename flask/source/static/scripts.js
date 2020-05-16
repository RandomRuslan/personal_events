function getFieldsData(wrapper) {
    let emptyError = false;
    let data = {}

    $('input, textarea', wrapper).each(function() {
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

function flushFields(wrapper) {
    $('input, textarea', wrapper).each(function() {
        $(this).removeClass('error').val('');
    });
}

let auth = {
    authWrapper: null,
    authBlock: null,
    signInButton: null,
    signUpButton: null,
    authMessage: null,

    signOutButton: null,

    eventCardTemplate: null,

    init: function () {
        this.authWrapper = $('#auth_wrapper');
        this.authBlock = $('#auth', this.authWrapper);
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
        let data = getFieldsData(this.authBlock);
        if (data) {
            $.post(method, data, this.afterAuth.bind(this));
        }
    },

    afterAuth: function(responseData) {
        console.log(responseData);
        this.authMessage.toggleClass('error', responseData.error);
        if (responseData.error) {
            this.authMessage.text(responseData.text);
        } else {
            this.authWrapper.removeClass('no-auth');
            events.showEvents(responseData.events)
        }
    },

    signOut: function () {
        $.post('/signout', {}, function (responseData) {
            flushFields(this.newEventWrapper);
            this.authWrapper.addClass('no-auth');
        }.bind(this));
    }
}

let events = {
    eventsWrapper: null,
    newEventOverlay: null,
    newEventWrapper: null,
    eventCardTemplate: null,
    eventMessage: null,
    showNewEventButton: null,
    addEventButton: null,
    closeNewEventButton: null,
    
    init: function () {
        this.eventsWrapper = $('#events_wrapper');
        this.newEventOverlay = $('#new_event_overlay', this.eventsWrapper);
        this.newEventWrapper = $('#new_event', this.newEventOverlay);
        this.eventCardTemplate = $('.event-card', this.eventsWrapper).remove();

        this.eventMessage = $('#event_message', this.authBlock);

        this.showNewEventButton = $('#show_new_event', this.eventsWrapper);
        this.showNewEventButton.click(this.showNewEvent.bind(this));

        this.addEventButton = $('#add_event', this.newEventOverlay);
        this.addEventButton.click(this.addEvent.bind(this));

        this.closeNewEventButton = $('.close-button', this.newEventOverlay);
        this.closeNewEventButton.click(this.closeNewEvent.bind(this));
    },

    showEvents: function(events) {
        events.forEach(function(event) {
            let el = this.eventCardTemplate.clone();
            el.attr('id', event.id);
            $('.event-date', el).html(event.date);
            $('.event-title', el).html(event.title);
            $('.event-note', el).html(event.note);
            this.eventsWrapper.append(el);
        }.bind(this))
    },

    showNewEvent: function () {
        this.newEventOverlay.show();
        this.showNewEventButton.hide();
    },

    closeNewEvent: function () {
        flushFields(this.newEventWrapper);
        this.eventMessage.html('');
        this.newEventOverlay.hide();
        this.showNewEventButton.show();
    },

    addEvent: function () {
        let data = getFieldsData(this.newEventWrapper);
        if (data) {
            data.ts = Date.parse(data.date + '@' + data.time)/1000;
            delete data.date;
            delete data.time;
            $.post('/add_event', data, function (responseData) {
                console.log(responseData);
                if (responseData.error) {
                    this.eventMessage.text(responseData.text);
                } else {
                    this.closeNewEvent();
                    events.showEvents([responseData.event])
                }
            }.bind(this));
        }
    }
}

$(document).ready(function () {
    auth.init();
    events.init();
})