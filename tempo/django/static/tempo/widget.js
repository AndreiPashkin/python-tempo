(function($) {
    "use strict";
    var BASE_TMPL =
        "<div class='tempo-base'>" +
        "    <div>" +
        "        <label>Repeats: " +
        "        <select class='tempo-base-repeats'>" +
        "            <option value='weekly'>Weekly</option>" +
        "            <option value='monthly'>Monthly</option>" +
        "        </select>" +
        "        </label>" +
        "    </div>" +
        "    <div class='tempo-base-form-container'></div>" +
        "</div>",
        WEEKLY_TMPL =
        "<form>" +
        "    <div>" +
        "        <div>Repeat on:</div>" +
        "        <div class='tempo-weekly-repeat-on-container'></div>" +
        "    </div>" +
        "</form>",
        WEEKLY_REPEAT_ON_SEGMENT_TMPL =
        "<select class='tempo-weekly-segment-repeat-on-weekday'></select>" +
        "<select class='tempo-weekly-segment-repeat-on-from'></select>" +
        "<select class='tempo-weekly-segment-repeat-on-to'></select>" +
        "<span class='tempo-weekly-repeat-on-segment-action'></span>",
        WEEKLY_SEGMENT_ADD_ACTION_TMPL =
        "<button type='button' class='button tempo-weekly-segment-add-action'>Add Hours</button>",
        WEEKLY_SEGMENT_REMOVE_ACTION_TMPL =
        "<button type='button' class='button tempo-weekly-segment-remove-action'>Remove</button>",
        MONTHLY_TMPL =
        "<form>" +
        "    <div>" +
        "        <label>" +
        "            Repeat on: " +
        "            <input type='text' name='tempo-monthly-repeat-on'/>" +
        "        </label>" +
        "    </div>" +
        "</form>";

    var
        WEEKDAYS = {'1': 'Mon', '2': 'Tue', '3': 'Wed', '4': 'Thu', '5': 'Fri',
                    '6': 'Sat', '7': 'Sun'},
        INTERVALS = {'0.0':  '12:00 am (midnight)',          '0.5': '12:30 am',
                     '1.0':  '1:00 am',  '1.5':  '1:30 am',  '2.0': '2:00 am',
                     '2.5':  '2:30am',   '3.0':  '3:00 am',  '3.5': '3:30 am',
                     '4.0':  '4:00 am',  '4.5':  '4:30 am',  '5.0': '5:00 am',
                     '5.5':  '5:30 am',  '6.0':  '6:00 am',  '6.5': '6:30 am',
                     '7.0':  '7:00 am',  '7.5':  '7:30 am',  '8.0': '8:00 am',
                     '8.5':  '8:30 am',  '9.0':  '9:00am',   '9.5': '9:30 am',
                     '10.0': '10:00 am', '10.5': '10:30 am', '11.0': '11:00am',
                     '11.5': '11:30 am', '12.0': '12:00 pm(noon)',
                     '12.5': '12:30 pm', '13.0': '1:00 pm',  '13.5': '1:30 pm',
                     '14.0': '2:00 pm',  '14.5': '2:30 pm',  '15.0': '3:00 pm',
                     '15.5': '3:30 pm',  '16.0': '4:00 pm',  '16.5': '4:30 pm',
                     '17.0': '5:00 pm',  '17.5': '5:30 pm',  '18.0': '6:00 pm',
                     '18.5': '6:30 pm',  '19.0': '7:00 pm',  '19.5': '7:30 pm',
                     '20.0': '8:00 pm',  '20.5': '8:30 pm',  '21.0': '9:00 pm',
                     '21.5': '9:30 pm',  '22.0': '10:00 pm',
                     '22.5': '10:30 pm', '23.0': '11:00 pm',
                     '23.5': '11:30 pm'};

    function TimeSegmentView(weekday, from, to) {
        this.element = $('<li/>', {'class': 'tempo-weekly-repeat-on-segment'});
        this.template = WEEKLY_REPEAT_ON_SEGMENT_TMPL;
        this.weekday = weekday || 1;
        this.from = from || 12.0;
        this.to = to || 23.5;
    }

    TimeSegmentView.prototype.render = function() {
        this.element.html(this.template);
        var key, option,
            weekdaySelect = this.element.find('.tempo-weekly-segment-repeat-on-weekday'),
            fromSelect = this.element.find('.tempo-weekly-segment-repeat-on-from'),
            toSelect = this.element.find('.tempo-weekly-segment-repeat-on-to');


        for (key in WEEKDAYS) {
            if (!WEEKDAYS.hasOwnProperty(key)) {
                continue;
            }
            weekdaySelect.append($('<option/>', {'value': key,
                                                 'text': WEEKDAYS[key]}));
        }
        for (key in INTERVALS) {
            if (!INTERVALS.hasOwnProperty(key)) {
                continue;
            }
            option = $('<option/>', {'value': key,
                                     'text': INTERVALS[key]});
            fromSelect.append(option);
            toSelect.append(option.clone());
        }

        weekdaySelect.val(this.weekday);
        fromSelect.val(this.from);
        toSelect.val(this.to);

        return this;
    };
    // Sets action for the element.
    // Takes jQuery element that represents an action as an argument.
    TimeSegmentView.prototype.setAction = function(action) {
        console.log('setAction');
        return this.element.find('.tempo-weekly-repeat-on-segment-action')
                           .empty()
                           .append(action);
    };

    TimeSegmentView.prototype.getValue = function() {
        return {
            'weekday': Number(this.element.find('.tempo-weekly-segment-repeat-on-weekday').val()),
            'from': Number(this.element.find('.tempo-weekly-segment-repeat-on-from').val()),
            'to': Number(this.element.find('.tempo-weekly-segment-repeat-on-to').val())
        };
    };

    TimeSegmentView.prototype.setValue = function(value) {
        this.element.find('.tempo-weekly-segment-repeat-on-weekday').val(value['weekday']);
        this.element.find('.tempo-weekly-segment-repeat-on-from').val(value['from']);
        this.element.find('.tempo-weekly-segment-repeat-on-to').val(value['to']);
    };

    function TimeSegmentsView() {
        this.element = $('<ul/>', {'class': 'tempo-weekly-repeat-on'});
        this.segments = [];
    }

    TimeSegmentsView.prototype.setRemoveAction = function(segment) {
        console.log('setRemoveAction');
        var action = $(WEEKLY_SEGMENT_REMOVE_ACTION_TMPL), that = this;
        action.click(function() {
            for(var i = that.segments.length - 1; i >= 0; i--) {
                if (that.segments[i] === segment) {
                   that.segments.splice(i, 1);
                }
            }
            segment.element.remove();
        });
        segment.setAction(action);
    };

    TimeSegmentsView.prototype.setAddAction = function(segment) {
        var action = $(WEEKLY_SEGMENT_ADD_ACTION_TMPL), that = this;
        action.click(function() {
            that.addSegment();
        });
        segment.setAction(action);
    };

    TimeSegmentsView.prototype.addSegment = function(weekday, from, to) {
        console.log('addSegment');
        var oldSegment = this.segments[this.segments.length - 1],
            newSegment = new TimeSegmentView(weekday, from, to);

        this.element.append(newSegment.render().element);
        this.segments.push(newSegment);
        this.setAddAction(newSegment);

        if (oldSegment) {
            this.setRemoveAction(oldSegment);
        }
        return newSegment;
    };

    TimeSegmentsView.prototype.getValue = function() {
        var i, values = [];
        for (i = 0; i < this.segments.length; i++) {
            values.push(this.segments[i].getValue());
        }
        return values;
    };

    TimeSegmentsView.prototype.setValue = function(value) {
        var i, segment;
        this.element.empty();
        this.segments.splice(0, this.segments.length);

        for(i = 0; i < value.length; i++) {
            this.addSegment(value[i]['weekday'], value[i]['from'], value[i]['to']);
        }
    };

    TimeSegmentsView.prototype.render = function() {
        this.element.empty();
        return this;
    };

    function WeeklyView() {
        this.element = $('<div/>', {'class': 'tempo-weekly'});
        this.template = WEEKLY_TMPL;
        this.timeSegmentsView = new TimeSegmentsView();
    }

    WeeklyView.prototype.render = function () {
        this.element.html(this.template);
        var that = this,
            repeatOn = this.element.find('.tempo-weekly-repeat-on-container');
        repeatOn.append(this.timeSegmentsView.render().element);
        this.timeSegmentsView.addSegment();
        return this;
    };

    WeeklyView.prototype.getValue = function() {
        return {
            'repeats': 'weekly',
            'repeatOn': this.timeSegmentsView.getValue()
        };
    };

    WeeklyView.prototype.setValue = function(value) {
        this.timeSegmentsView.setValue(value.repeatOn)
    };

    function MonthlyView(repeatOn) {
        this.element = $('<div/>', {'class': 'tempo-monthly'});
        this.template = MONTHLY_TMPL;
        this.repeatOn = repeatOn || 1;
    }

    MonthlyView.prototype.render = function() {
        this.element.empty();
        this.element.html(this.template);
        var that = this,
            repeatOn = this.element.find('input[name="tempo-monthly-repeat-on"]');

        repeatOn.val(this.repeatOn); // Set default value
        repeatOn.change(function() {
            that.repeatOn = Number(repeatOn.val());
        });

        return this;
    };

    MonthlyView.prototype.getValue = function () {
        return {
            'repeats': 'monthly',
            'repeatOn': Number(this.repeatOn)
        };
    };

    MonthlyView.prototype.setValue = function(value) {
        this.repeatOn = value.repeatOn;
        this.element
                .find('input[name="tempo-monthly-repeat-on"]')
                .val(this.repeatOn);
    };

    $.fn.tempo = function(value) {
        var base = $(BASE_TMPL), that = this;
        this.after(base);

        value = value || {
            'repeats': 'weekly',
            'repeatOn': [
                {'weekday': 1, 'from': 12.0, 'to': 23.5}
            ]
        };

        var repeats = base.find('.tempo-base-repeats'),
            container = base.find('.tempo-base-form-container'),
            view;
        repeats.val(value.repeats);

        function repeatsChangeHandler() {
            if (repeats.val() === 'weekly') {
                view = new WeeklyView();
                container.html(view.render().element);
            } else if (repeats.val() === 'monthly') {
                view = new MonthlyView();
                container.html(view.render().element);
            }
            return view;
        }
        repeats.change(repeatsChangeHandler);
        repeatsChangeHandler().setValue(value);

        base.on('click change blur keyup', function() {
            var value = view.getValue();
            console.log(value);
            that.val(JSON.stringify(value));
        });
    };
}(django.jQuery));
