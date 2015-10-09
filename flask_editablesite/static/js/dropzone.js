Dropzone.autoDiscover = false;

(function($, window) {

  var dropzone_dict_default_message = 'Drop image here or click to upload.';

  $('.dropzone-to-enable').each(function() {
    $(this).addClass('dropzone');

    var thumbDim = (
        $(this).closest('.jumbotron').length ? 256 : (
        $(this).closest('.modal-content').length ? 1200 : 72));

    var thumbWidth = thumbDim;

    var thumbHeight = (
        $(this).closest('.modal-content').length ? 900 : thumbDim);

    $(this).dropzone({
      url: $(this).attr('action').replace('/image-update/', '/image-update-dropzone/'),
      dictDefaultMessage: dropzone_dict_default_message,
      uploadMultiple: false,
      paramName: 'image',
      thumbnailWidth: thumbWidth,
      thumbnailHeight: thumbHeight
    });
  });

}).call(this, jQuery, window);
