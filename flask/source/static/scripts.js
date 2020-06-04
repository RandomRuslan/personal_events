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

    EventManager.setLocationHash(null);
    EventFilter.flushFilters()
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

    let minutes = getTwoCharFormat(date.getMinutes());
    let hours = getTwoCharFormat(date.getHours());
    let day = getTwoCharFormat(date.getDate());
    let month = getTwoCharFormat(date.getMonth() + 1);
    let year = date.getFullYear();
    return [
        year + '-' + month + '-' + day,
        hours + ":" + minutes
    ];
}

let AuthManager = {
    eventManager: null,

    authWrapper: null,
    authBlock: null,
    signInButton: null,
    signUpButton: null,
    authErrorMessage: null,

    signOutButton: null,

    eventCardTemplate: null,

    init: function (eventManager) {
        this.eventManager = eventManager;

        this.authWrapper = $('#auth_wrapper');
        this.authBlock = $('#auth', this.authWrapper);
        this.signInButton = $('#sign_in', this.authBlock);
        this.signUpButton = $('#sign_up', this.authBlock);
        this.authErrorMessage = $('#auth_error', this.authBlock);

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
        this.authErrorMessage.toggle(responseData.error);
        if (responseData.error) {
            this.authErrorMessage.text(responseData.text);
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

    eventFilter: null,
    
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
        $('#set_event', this.eventOverlay).click(this.setEvent.bind(this));
        $('.close-button', this.eventOverlay).click(this.closeEventForm.bind(this));

        $('.event-card', this.eventsWrapper).click(this.focusOnCard.bind(this));
        $('.edit-event', this.eventsWrapper).click(this.editEvent.bind(this));
        $('.delete-event', this.eventsWrapper).click(this.deleteEvent.bind(this));

        this.eventFilter = EventFilter.init(this);

        let hash = location.hash;
        if (hash) {
            this.setCardChoice(hash.slice(1));
        }

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

        this.setLocationHash(el.attr('id'));
        this.eventFilter.flushFilters();
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

        el.click(this.focusOnCard.bind(this));
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

    setEvent: function () {
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
        let card = $(e.target).closest('.event-card');
        let data = {'cardid': card.attr('id')};
        
        $('[data-key]', card).each(function() {
            let cardField = $(this);
            data[cardField.data('key')] = cardField.text();
        });

        this.showEventForm(data);
    },

    deleteEvent: function (e) {
        let card = $(e.target).closest('.event-card');
        let cardId = card.attr('id');
        $.post('/delete_event', {'cardId': cardId}, function (responseData) {
            if (responseData.error) {
                alert(responseData.text);
            } else {
                card.remove();
                this.setLocationHash(null);
            }
        }.bind(this));
    },

    focusOnCard: function (e) {
        this.setLocationHash($(e.currentTarget).attr('id'));
    },

    setLocationHash: function(hash) {
        let scrollPosition = this.eventsWrapper.scrollTop();
        location.hash = hash || '';
        this.eventsWrapper.scrollTop(scrollPosition);

        this.setCardChoice(hash);
    },

    setCardChoice: function (id) {
        $('.event-card.chosen', this.eventsWrapper).removeClass('chosen');
        if (id) {
            $('.event-card#' + id, this.eventsWrapper).addClass('chosen');
        }
    }
}

let EventFilter = {
    eventManager: null,

    filterWrapper: null,

    periodSelect: null,
    fromInput: null,
    toInput: null,
    titleInput: null,

    init: function (eventManager) {
        this.eventManager = eventManager;
        this.filterWrapper = $('#event_filter', eventManager.eventsWrapper);

        this.periodSelect = $('select', this.filterWrapper);
        this.fromInput = $('input[name="from"]', this.filterWrapper);
        this.toInput = $('input[name="to"]', this.filterWrapper);
        this.titleInput = $('input[name="title-filter"]', this.filterWrapper);

        $('input', this.filterWrapper).change(this.onInputManualChange.bind(this));
        this.periodSelect.change(this.onSelectChange.bind(this));

        $('.filter-button', this.filterWrapper).click(this.onClickFilterButton.bind(this));

        return this;
    },

    switchFilterButton: function(button, switchTo) {
        button.toggleClass('clicked', switchTo !== undefined ? switchTo : !button.hasClass('clicked'));
        this.applyFilters();
    },

    onClickFilterButton: function(e) {
        let filterButton = $(e.target);
        let filterBlock = filterButton.closest('.filter-block');

        let hasEmptyInput = false;
        $('input', filterBlock).each(function (index, filterInput) {
            filterInput = $(filterInput);
            if (!filterInput.val()) {
                filterInput.addClass('error');
                hasEmptyInput = true;
            } else {
                filterInput.removeClass('error');
            }
        }.bind(this));

        this.switchFilterButton(filterButton, hasEmptyInput ? false : undefined);
    },

    onInputManualChange: function(e) {
        let filterInput = $(e.target);
        let filterBlock = filterInput.closest('.filter-block');
        let filterButton = $('.filter-button', filterBlock);
        let filterType = filterButton.data('type');

        filterInput.removeClass('error');
        
        if (filterType === 'period') {
            this.selectPeriodOption('-');
        }
        
        this.switchFilterButton(filterButton, false);
    },

    onSelectChange: function(e) {
        let period = $(':selected', this.periodSelect).data('period');
        this.selectPeriodOption(period);

        let dates = this.getPeriodDates(period);
        this.fromInput.val(dates[0]);
        this.toInput.val(dates[1]);
        
        let filterBlock = $(e.target).closest('.filter-block');
        let filterButton = $('.filter-button', filterBlock);

        this.switchFilterButton(filterButton, false);
    },

    selectPeriodOption: function(period) {
        $('option', this.periodSelect).attr('selected', false);
        $('[data-period="' + period + '"]', this.periodSelect).attr('selected', true);
    },

    getPeriodDates: function (period) {
        let from = new Date();
        let to = new Date();

        switch (period) {
            case 'd':
                from.setTime(from.getTime() - 60 * 60 * 24 * 1000);
                break;
            case 'w':
                from.setTime(from.getTime() - 60 * 60 * 24 * 7 * 1000);
                break;
            case 'm':
                let month = from.getMonth();
                if (month === 0) {
                    from.setFullYear(from.getFullYear() - 1);
                    from.setMonth(11);
                } else {
                    from.setMonth(month - 1);
                }
                break;
            case 'y':
                from.setFullYear(from.getFullYear() - 1)
                break;
            case '-':
            default:
                return ['', '']
        }

        return [
            convertTsToDate(from.getTime() / 1000)[0],
            convertTsToDate(to.getTime() / 1000)[0]
        ];
    },

    applyFilters: function () {
        this.eventManager.setLocationHash(null);
        let cards = $('.event-card', this.eventManager.eventsWrapper);
        cards.show();

        $('.filter-button.clicked', this.filterWrapper).each(function (index, button) {
            button = $(button);
            let filterType = button.data('type');
            switch (filterType) {
                case('period'):
                    cards.each(function (index, card) {
                        card = $(card);
                        let ts = card.data('ts');

                        let fromDate = this.fromInput.val();
                        let toDate = this.toInput.val();
                        if (fromDate > toDate) {
                            [fromDate, toDate] = [toDate, fromDate];
                            this.fromInput.val(fromDate);
                            this.toInput.val(toDate);
                        }

                        let fromTs = Date.parse(fromDate + '@00:00:00')/1000;
                        let toTs = Date.parse(toDate + '@23:59:59')/1000;

                        if (ts < fromTs || toTs < ts) {
                            card.hide();
                        }
                    }.bind(this));
                    break;
                case('title'):
                    let titleFilter = this.titleInput.val().toLocaleLowerCase();
                    cards.each(function (index, card) {
                        card = $(card);
                        let cardTitle = $('.event-title', card).text().toLocaleLowerCase();
                        if (cardTitle.indexOf(titleFilter) === -1) {
                            card.hide();
                        }
                    }.bind(this));
                    break;
                default:
                    console.log('Unknown filter type:', filterType);
            }
        }.bind(this));
    },

    flushFilters: function () {
        $('.filter-button.clicked').each(function() {
            $(this).removeClass('clicked');
        });

        this.applyFilters();
    }
}

$(document).ready(function () {
    let eventManager = EventManager.init();
    AuthManager.init(eventManager);
})