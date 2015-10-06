(function($, window) {

  $('.form-editable-button').addClass('hidden');

  $('.title-image-wrapper .editable-wrapper, .dante-editable').each(function() {
    if ($(this).find('#start_date, #end_date').length) {
      $(this).before('<div class="edit-icon-wrapper"><span class="glyphicon glyphicon-calendar"></span></div>');
    }
    else if ($(this).find('#start_time, #end_time').length) {
      $(this).before('<div class="edit-icon-wrapper"><span class="glyphicon glyphicon-time"></span></div>');
    }
    else if ($(this).hasClass('dante-editable')) {
      $(this).before('<div class="edit-icon-wrapper edit-icon-dante"><span class="glyphicon glyphicon-pencil"></span></div>');
    }
    else {
      $(this).before('<div class="edit-icon-wrapper"><span class="glyphicon glyphicon-pencil"></span></div>');
    }
  });

  $('.title-image-wrapper .editable-wrapper, .dante-editable')
    .hover(function() {
      var editableEl = $(this);
      if (!$(this).hasClass('dante-editable')) {
        editableEl = editableEl.find('input[type=text]');
      }

      editableEl.addClass('active');
      if (!$(this).hasClass('dante-editable')) {
        $(this).prev('.edit-icon-wrapper').find('.glyphicon').wrap('<a />');
      }
      else {
        $(this).closest('.postArticle').prev('.edit-icon-wrapper').find('.glyphicon').wrap('<a />');
      }
    },
    function() {
      var editableEl = $(this);
      if (!$(this).hasClass('dante-editable')) {
        editableEl = editableEl.find('input[type=text]');
      }

      editableEl.removeClass('active');
      if (!$(this).hasClass('dante-editable')) {
        if ($(this).prev('.edit-icon-wrapper').find('.glyphicon').parent('a').length) {
          $(this).prev('.edit-icon-wrapper').find('.glyphicon').unwrap();
        }
      }
      else {
        if ($(this).closest('.postArticle').prev('.edit-icon-wrapper').find('.glyphicon').parent('a').length) {
          $(this).closest('.postArticle').prev('.edit-icon-wrapper').find('.glyphicon').unwrap();
        }
      }
    });

}).call(this, jQuery, window);
