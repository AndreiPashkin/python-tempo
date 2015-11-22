(function($) {
  "use strict";

  var
    OPS = ['OR', 'AND', 'NOT'],
    RECURRENT_EVENT_SET =
      "<div class='tempo-recurrenteventset'>" +
      "<div class='tempo-recurrenteventset-operator'>" +
      "<a href='#' class='tempo-recurrenteventset-remove'>-</a>" +
      "<select>" +
      "<option value='AND'>And</option>" +
      "<option value='OR'>Or</option>" +
      "<option value='NOT'>Not</option>" +
      "</select>" +
      "</div>" +
      "<div class='tempo-recurrenteventset-operands'></div>" +
      "<div class='tempo-recurrenteventset-controls'>" +
      "<a href='#' class='tempo-recurrenteventset-add'>+ Recurrent Event</a>" +
      "<a href='#' class='tempo-recurrenteventset-addset'>+ Recurrent Event Set</a>" +
      "</div>" +
      "</div>",
    RECURENT_EVENT =
      "<div class='tempo-recurrentevent'>"+
      "<a href='#' class='tempo-recurrentevent-remove'>-</a>" +
      "between " +
      "<input placeholder='10' type='text' class='tempo-recurrentevent-from' /> " +
      "to <input placeholder='12' type='text' class='tempo-recurrentevent-to' /> " +
      "<select class='tempo-recurrentevent-unit'>" +
      "<option value='second'>Second</option>" +
      "<option value='minute'>Minute</option>" +
      "<option value='hour' selected='true'>Hour</option>" +
      "<option value='day'>Day</option>" +
      "<option value='week'>Week</option>" +
      "<option value='month'>Month</option>" +
      "<option value='year'>Year</option>" +
      "<select/>" +
      " every " +
      "<select class='tempo-recurrentevent-recurrence'>" +
      "<option value='second'>Second</option>" +
      "<option value='minute'>Minute</option>" +
      "<option value='hour'>Hour</option>" +
      "<option value='day' selected='true'>Day</option>" +
      "<option value='week'>Week</option>" +
      "<option value='month'>Month</option>" +
      "<option value='year'>Year</option>" +
      "<option value='null'>None</option>" +
      "</select>" +
      "</div>",
    DEFAULT_RECURRENT_EVENT = [10, 12, 'hour', 'day'],
    DEFAULT_RECURRENT_EVENT_SET = ['OR', []];

  function RecurrentEventSet(input) {
    var that = this;

    this.input = $(input);
    this.node = $(RECURRENT_EVENT_SET);
    this.input.before(this.node);

    this.node.find('.tempo-recurrenteventset-remove').click(function() {
      that.node.remove();
      that.input.val('').change();
    });

    this.node.children('.tempo-recurrenteventset-controls')
             .children('.tempo-recurrenteventset-add')
             .click(function() {
               that.addRecurrentEvent();
             });
    this.node.children('.tempo-recurrenteventset-controls')
             .children('.tempo-recurrenteventset-addset')
             .click(function() {
               that.addRecurrentEventSet(DEFAULT_RECURRENT_EVENT_SET);
             });

    var value = this.input.val(), expression;

    if (value) {
      expression = JSON.parse(this.input.val());
    } else {
      expression = DEFAULT_RECURRENT_EVENT_SET;
    }

    if (OPS.indexOf(expression[0].toUpperCase()) === -1) {
      throw new TypeError('Wrong expression format. Got: "'+
                          expression +
                          '".');
    }

    this.node.children('.tempo-recurrenteventset-operator')
             .children('select')
             .val(expression[0]);

    var i, element;
    for (i = 1; i < expression.length; i++) {
      element = expression[i];
      if (element.length > 0 && typeof element[0] === 'string' &&
          OPS.indexOf(element[0].toUpperCase()) !== -1) {
        this.addRecurrentEventSet(element);
      } else {
        this.addRecurrentEvent(element);
      }
    }
  }
  RecurrentEventSet.prototype.addRecurrentEvent = function(expression) {
    var recurrentEvent = $(RECURENT_EVENT);

    if (expression && expression.length === 4) {
      recurrentEvent.find('.tempo-recurrentevent-from').val(expression[0]);
      recurrentEvent.find('.tempo-recurrentevent-to').val(expression[1]);
      recurrentEvent.find('.tempo-recurrentevent-unit').val(expression[2]);
      recurrentEvent.find('.tempo-recurrentevent-recurrence').val(expression[3]);
    }
    recurrentEvent.children('.tempo-recurrentevent-remove').click(function() {
      recurrentEvent.remove();
    });

    this.node.children('.tempo-recurrenteventset-operands').append(recurrentEvent);
  };
  RecurrentEventSet.prototype.addRecurrentEventSet = function(expression) {
    var input = $('<input type="hidden" />'),
        recurrentEventSet;

    if (typeof expression !== 'string') {
      expression = JSON.stringify(expression);
    }
    input.val(expression);
    recurrentEventSet = new RecurrentEventSet(input);

    this.node.children('.tempo-recurrenteventset-operands')
             .append(recurrentEventSet.node);
  };
  function getValue(node) {
    var expression = [];
    expression[0] = node.children('.tempo-recurrenteventset-operator')
                        .children('select')
                        .val();
    node
      .children('.tempo-recurrenteventset-operands')
      .children()
      .each(function() {
        var operand = $(this), from, to, unit, recurrence;
        if (operand.hasClass('tempo-recurrentevent')) {
          from = (+operand.children('.tempo-recurrentevent-from').val());
          to = (+operand.children('.tempo-recurrentevent-to').val());
          unit = operand.children('.tempo-recurrentevent-unit').val();
          recurrence = operand.children('.tempo-recurrentevent-recurrence').val();
          expression.push([from, to, unit, recurrence]);
        } else if (operand.hasClass('tempo-recurrenteventset')) {
          expression.push(getValue(operand));
        } else {
          throw new Error('Unexpected operand.');
        }
      });
    return expression;
  }

  $.fn.tempo = function(value) {
    var that = this;
    if (typeof value === 'string' && value.toUpperCase() === 'destroy') {
      $(this).trigger('tempo-destroy');
      return;
    }
    if (typeof value === 'string') {
      $(this).val(value);
      value = JSON.parse(value);
    }

    var recurrentEventSet = new RecurrentEventSet(this), subscribed;
    $(this).on('tempo-destroy', function() {
      recurrentEventSet.node.remove();
      $(that).val('');
    })
    function updateValue(event) {
      console.log(event);
      var value = getValue(recurrentEventSet.node);
      $(that).val(JSON.stringify(value));
      if (subscribed) {
        subscribed.off('change click', updateValue);
      }
      subscribed = recurrentEventSet.node.find('input, select, a');
      subscribed.on('change click', updateValue)
    }
    updateValue();
  }
}(django.jQuery));
