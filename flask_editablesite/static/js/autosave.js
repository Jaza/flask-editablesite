(function($, _, window) {

  // How long to wait (in milliseconds) for a user to stop typing,
  // before attempting to do an autosave.
  var pendingDelayInMs = 2000;

  // Don't need to try and manually check if the full delay has elapsed
  // since last user input, Underscore.js debounce() gives us this for free.
  var autosaveAfterDelay = _.debounce(
    function($this, autosaveUrl) {
      // More than 'x' ms has passed since the user last inputted
      // something, so we can stop pending.
      $this.removeAttr('data-autosave-pending');

      $this.attr('data-autosave-inprogress', '1');

      // Alert the user that an autosave is now in progress.
      if (!($this.find('.autosave-status').html() == 'Saving')) {
        $this.find('.autosave-status')
          .html('Saving')
          .removeClass('alert-success')
          .addClass('alert-warning');
      }

      var postData = $this.serializeArray();

      // Attempt to perform the autosave via AJAX.
      $.ajax({
        url: autosaveUrl,
        type: 'POST',
        data: postData,
        success: function(data, textStatus, jqXHR) {
          $this.removeAttr('data-autosave-inprogress');

          if (data == 'OK') {
            // Yay! Autosave worked.
            if (!($this.find('.autosave-status').html() == 'Saved')) {
              $this.find('.autosave-status')
                .html('Saved')
                .removeClass('alert-warning')
                .addClass('alert-success');
            }
          }
          else {
            // Autosave failed because of some validation
            // failing in server submit handler.
            $this.find('.autosave-status')
              .html('Autosave failed: ' + data)
              .removeClass('alert-warning')
              .addClass('alert-danger');
          }
        },
        error: function(jqXHR, textStatus, errorThrown) {
          $this.removeAttr('data-autosave-inprogress');

          var errorMsg = 'Autosave failed: ';
          if (errorThrown) {
            // Autosave failed due to server returning
            // bad status (probably 500 error).
            errorMsg += 'server encountered an error';
          }
          else {
            // Autosave failed due to server not being
            // reached (probably network error).
            errorMsg += 'couldn\'t connect to server';
          }

          $this.find('.autosave-status')
            .html(errorMsg)
            .removeClass('alert-warning')
            .addClass('alert-danger');
        }});
    },
    pendingDelayInMs);

  $('form[data-autosave-url][data-autosave-field-id]').each(function() {
    var $this = $(this);
    var autosaveUrl = $(this).attr('data-autosave-url');
    var elId = '#' + $(this).attr('data-autosave-field-id');
    var isElOptional = !($(this).attr('required'));

    $(this).find(':input, .dante-editable').on('input', function(e) {
      // Submission content is required by server-side validation,
      // so don't try to autosave if it's not set yet.
      if (!$this.find(elId).val() && !isElOptional) {
        $this.find('.autosave-status')
          .html('No autosave while content is blank')
          .removeClass('alert-success')
          .removeClass('alert-danger')
          .addClass('alert-warning');
      }

      // Don't autosave now if another autosave is already in progress.
      if (($this.find(elId).val() || isElOptional) && !$this.attr('data-autosave-inprogress')) {
        $this.attr('data-autosave-pending', '1');

        // While we're pending, alert the user that they have
        // unsaved changes at this time.
        if (!($this.find('.autosave-status').html() == 'Unsaved changes')) {
          $this.find('.autosave-status')
            .html('Unsaved changes')
            .removeClass('alert-success')
            .removeClass('alert-danger')
            .addClass('alert-warning');
        }

        // Every 'x' ms (determined by pendingDelayInMs), see if
        // we can do an autosave.
        autosaveAfterDelay($this, autosaveUrl);
      }
    });

    // Toggle autosave status box visibility depending on when an
    // input box has focus.
    $(this).find(':input, .dante-editable')
      .focus(function(e) {
        $this.find('.autosave-status-wrapper').show();
        })
      .blur(function(e) {
        $this.find('.autosave-status-wrapper').hide();
      });
  });

}).call(this, jQuery, _, window);
