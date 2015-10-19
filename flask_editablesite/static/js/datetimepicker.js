(function($, window) {

  $('.datepicker-enable').datetimepicker({
    format: 'DD MMM YYYY'});

  $('.timepicker-enable').datetimepicker({
    format: 'HH:mm'});

  $('.datepicker-enable, .timepicker-enable').on('dp.change', function(e) {
      $(this)
        .trigger('input');
    });

}).call(this, jQuery, window);
