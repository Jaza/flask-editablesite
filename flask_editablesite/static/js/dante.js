(function($, window) {

  function updateDanteFromTextareas(event) {
    var ta = $(event.target);
    if (((event.type == 'keyup' || event.type == 'paste') && ta.is(':focus')) || event.type == 'blur') {
      var elem_jq = $('#' + ta.attr('id') + '-wysiwyg');
      elem_jq.html(ta.val());
    }
  }

  var elements = document.querySelectorAll('.dante-editable');

  $.each(elements, function(i, elem) {
    var elem_jq = $(elem);
    var elem_id = elem_jq.attr('id');
    var ta_id = elem_id.replace('-wysiwyg', '');
    var ta = elem_jq.siblings('#' + ta_id);

    if (ta.val()) {
      elem_jq.html(ta.val());
    }

    var dante_editor_options = {
      el: elem,
      upload_url: null,
      debug: false
    };

    var editor = new Dante.Editor(dante_editor_options);
    editor.start();

    $('body').on('input', elem_jq, function(event) {
      var c = editor.cleanContents(elem_jq
          .find('.section-inner')
          .clone())
        .html()
        .replace(/\<br\>\<\/p\>/g, '</p>')
        .replace(/ class=\"[^\"]+\"/g, '');

      ta.val(c)
        .trigger('keyup');
    });

    ta.hide();
    /*$('body').on('blur keyup paste', ta, updateDanteFromTextareas);

    if (ta.val()) {
      elem_jq.trigger('click');
    }*/
  });

}).call(this, jQuery, window);
