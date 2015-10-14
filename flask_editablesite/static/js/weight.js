(function($, window) {
  $('body').on('click', '.weight-move-up, .weight-move-down', function() {
    var weightItem = $(this).closest('.weight-item');
    var weightFormItemId = null;
    var weightFormItem = null;
    var weightFormGroup = null;

    if (weightItem.attr('id') && /^for\-/.test(weightItem.attr('id')) && /\-weight$/.test(weightItem.attr('id'))) {
      weightFormItemId = weightItem.attr('id').replace('for-', '');
      weightFormItem = $('#' + weightFormItemId);

      if (weightFormItem.length) {
        weightFormGroup = weightFormItem.parent('.form-group');
      }
    }

    if ($(this).hasClass('weight-move-up')) {
      weightItem.prev('.weight-item').before(weightItem);

      if (weightFormGroup) {
        weightFormGroup.prev('.form-group').before(weightFormGroup);
      }
    }
    else {
      weightItem.next('.weight-item').after(weightItem);

      if (weightFormGroup) {
        weightFormGroup.next('.form-group').after(weightFormGroup);
      }
    }

    var currWeight = 0;
    var weightItems = weightItem.parent('.weight-sortable').children('.weight-item');

    if (weightFormGroup && weightFormGroup.siblings('button[type="submit"].hidden').length) {
      weightFormGroup.siblings('button[type="submit"].hidden').removeClass('hidden');
    }

    weightItems.each(function(i, v) {
      weightItem = $(this);
      weightFormItemId = null;
      weightFormItem = null;
      weightFormGroup = null;

      if (weightItem.attr('id') && /^for\-/.test(weightItem.attr('id')) && /\-weight$/.test(weightItem.attr('id'))) {
        weightFormItemId = weightItem.attr('id').replace('for-', '');
        weightFormItem = $('#' + weightFormItemId);

        if (weightFormItem.length) {
          weightFormGroup = weightFormItem.parent('.form-group');
        }
      }

      if (weightFormItem) {
        $(weightFormItem).val(currWeight);
      }
      else {
        $(this).find('input[type="hidden"][id$="-weight"]').val(currWeight);
      }

      currWeight += 1;

      if ($(this).find('.weight-humanized').length) {
        $(this).find('.weight-humanized').html(currWeight + '.');
      }

      var newControls = '';

      if (i) {
        newControls += '<a href="#" class="btn btn-primary weight-move-up" title="Move up"><span class="glyphicon glyphicon-arrow-up" aria-hidden="true"></span></a> ';
      }

      if (i != weightItems.length-1) {
        newControls += '<a href="#" class="btn btn-primary weight-move-down" title="Move down"><span class="glyphicon glyphicon-arrow-down" aria-hidden="true"></span></a> ';
      }

      $(this).find('.weight-controls').html(newControls);
    });

    return false;
  });
}).call(this, jQuery, window);
