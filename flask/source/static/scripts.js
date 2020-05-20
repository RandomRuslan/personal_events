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

function flashPage() {
    flushFields(document);
    $('.event-card').remove();
}

function flushFields(wrapper) {
    $('input, textarea', wrapper).each(function() {
        $(this).removeClass('error').val('');
    });
}

function convertTsToDate(ts) {
    function getTwoCharFormat(number) {
        number = '0' + number;
        return number.substr(-2);
    }

    let date = new Date();
    date.setTime(ts * 1000);

    let seconds = getTwoCharFormat(date.getSeconds());
    let minutes = getTwoCharFormat(date.getMinutes());
    let hours = getTwoCharFormat(date.getHours());
    let day = getTwoCharFormat(date.getDate());
    let month = getTwoCharFormat(date.getMonth() + 1);
    let year = date.getFullYear();
    return [
        year + '-' + month + '-' + day,
        hours + ":" + minutes + ":" + seconds
    ];
}

let AuthManager = {
    eventManager: null,

    authWrapper: null,
    authBlock: null,
    signInButton: null,
    signUpButton: null,
    authMessage: null,

    signOutButton: null,

    eventCardTemplate: null,

    init: function (eventManager) {
        this.eventManager = eventManager;

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
            this.eventManager.showLoadedEvents(responseData.events);
        }
    },

    signOut: function () {
        $.post('/signout', {}, function (responseData) {
            flashPage();
            this.authWrapper.addClass('no-auth');
        }.bind(this));
    }
}

let EventManager = {
    eventCardTemplate: null,

    eventsWrapper: null,
    eventOverlay: null,
    setEventForm: null,

    eventMessage: null,
    cardIdInputTemplate: null,
    
    init: function () {
        this.eventsWrapper = $('#events_wrapper');
        this.eventOverlay = $('#event_overlay', this.eventsWrapper);
        this.setEventForm = $('#settable_event', this.eventOverlay);
        this.eventCardTemplate = $('.event-card-template', this.eventsWrapper)
            .removeClass('event-card-template')
            .remove();

        this.eventMessage = $('#event_message', this.authBlock);
        this.cardIdInputTemplate = $('#card_id', this.eventOverlay).remove();

        $('#show_event_overlay', this.eventsWrapper).click(function () { this.showEventForm() }.bind(this));
        $('#set_event', this.eventOverlay).click(this.addEvent.bind(this));
        $('.close-button', this.eventOverlay).click(this.closeEventForm.bind(this));

        $('.edit-event', this.eventsWrapper).click(this.editEvent.bind(this));
        $('.delete-event', this.eventsWrapper).click(this.deleteEvent.bind(this));

        return this;
    },

    showNewEvent: function(event) {
        let el = this.prepareEventElement(event);
        let isInsert = false;

        $('.event-card', this.eventsWrapper).each(function(index, event) {
            event = $(event);
            if (event.data('ts') < el.data('ts')) {
                event.before(el);
                isInsert = true;
                return false;
            }
        });

        if (!isInsert) {
            this.eventsWrapper.append(el);
        }
    },

    showLoadedEvents: function(events) {
        events.forEach(function(event) {
            this.eventsWrapper.append(this.prepareEventElement(event));
        }.bind(this))
    },
    
    prepareEventElement: function(event) {
        let el = this.eventCardTemplate.clone();
        el.attr('id', event.cardId);
        el.data('ts', event.ts);

        let date = convertTsToDate(event.ts);
        $('.event-date', el).html(date[0]);
        $('.event-time', el).html(date[1]);

        $('.event-title', el).html(event.title);
        $('.event-note', el).html(event.note);

        $('.edit-event', el).click(this.editEvent.bind(this));
        $('.delete-event', el).click(this.deleteEvent.bind(this));

        return el;
    },

    showEventForm: function (data) {
        if (data) {
            this.setEventForm.append(this.cardIdInputTemplate.clone());
            $('input, textarea', this.setEventForm).each(function() {
                let overlayField = $(this);
                let key = overlayField.attr('name');
                overlayField.val(data[key]).data('oldValue', data[key]);
            });
        }
        this.eventOverlay.show();
    },

    closeEventForm: function () {
        flushFields(this.setEventForm);
        this.eventMessage.html('');
        $('#card_id', this.setEventForm).remove();
        this.eventOverlay.hide();
    },

    isNewData: function() {
        let isAnyNewData = false;
        $('input, textarea', this.setEventForm).each(function() {
            let el = $(this);
            if (el.val() !== el.data('oldValue')) {
                isAnyNewData = true;
                return false;
            }
        })
        return isAnyNewData;
    },

    addEvent: function () {
        let data = getFieldsData(this.setEventForm);
        if (data) {
            let cardId = data.cardid;
            if (cardId && !this.isNewData()) {
                this.eventMessage.text('New data is required');
                return;
            }
            data.ts = Date.parse(data.date + '@' + data.time)/1000;
            data.tz = new Date().getTimezoneOffset() / 60;
            delete data.date;
            delete data.time;

            $.post('/set_event', data, function (responseData) {
                console.log(responseData);
                if (responseData.error) {
                    this.eventMessage.text(responseData.text);
                } else {
                    if (cardId) {
                        $('#' + cardId, this.eventsWrapper).remove();
                    }
                    this.closeEventForm();
                    this.showNewEvent(responseData.event);
                }
            }.bind(this));
        }
    },

    editEvent: function (e) {
        let card = $(e.target.parentElement);
        let data = {'cardid': card.attr('id')};
        
        $('[data-key]', card).each(function() {
            let cardField = $(this);
            data[cardField.data('key')] = cardField.text();
        });

        this.showEventForm(data);
    },

    deleteEvent: function (e) {
        let card = e.target.parentElement;
        let cardId = card.getAttribute('id');
        $.post('/delete_event', {'cardId': cardId}, function (responseData) {
            if (responseData.error) {
                alert(responseData.text);
            } else {
                card.remove();
            }
        }.bind(this));
    }
}

$(document).ready(function () {
    let eventManager = EventManager.init();
    AuthManager.init(eventManager);
})