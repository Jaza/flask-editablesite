(function($, window) {
  $('.delete-confirm-link').click(function(e) {
    var $this = $(this);

    if ($(this).attr('data-delete-confirm-item-type')) {
      e.preventDefault();

      bootbox.confirm('Are you sure you want to ' + $(this).attr('data-delete-confirm-item-type') + '? This operation cannot be undone.', function(result) {
        if (result) {
          $this.parent('form').submit();
        }
      });
    }
  });
}).call(this, jQuery, window);
