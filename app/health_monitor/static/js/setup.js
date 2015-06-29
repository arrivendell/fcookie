$(document).ready(function() {

    bindSensors();



})




var bindSensors = function() {

    // Expanding a service's view (by clicking on its heading)
    $('.services').on('click', 'li .heading', function(e) {
        $li = $(this).closest('li');
        $('.services li').not($li).find('.details').hide(200);

        $li.find('.details').stop();

        $li.find('.details').toggle(400);

    });

    // Activating the right callbacks' list
    $('.services').on('change', 'select[name="actuator"]', function(e) {
        $('select[name="callback"]').prop('disabled', true);
        $('select[name="callback"][data-actuator-id="' + $(this).val() + '"]').prop('disabled', false);
    });

    // s = $('select[name="callback"][data-actuator-id="889977"]')


    $('.services').on('slide', '.trigger-slider', function(ev){
        var $this = $(this);
        var min = $this.data('slider').value[0];
        var max = $this.data('slider').value[1];
        $(this).parent().parent().find('.threshold-trigger-min').text(min);
        $(this).parent().parent().find('.threshold-trigger-max').text(max);
    });


    $('.services').on('slideStop', '.trigger-slider .modify', function(ev){
        var $this = $(this);
        var min = $this.data('slider').value[0];
        var max = $this.data('slider').value[1];
        var thermometer_id = $this.closest('.service').data('service-id')
        $(this).parent().parent().find('.threshold-trigger-min').text(min);
        $(this).parent().parent().find('.threshold-trigger-max').text(max);

        //apiCall(...)
        //
    });

    $('.services').on('click', '.threshold-trigger .add', function(ev){
        var $this = $(this);
        var thermometer_id = $this.closest('.service').data('service-id')
        var threshold_name = $(this).closest('li').find('.threshold-trigger .name').val();
        var min = $(this).closest('li').find('.trigger-slider').data('slider').value[0]
        var max = $(this).closest('li').find('.trigger-slider').data('slider').value[1]

        console.log("min = " + min + "; max = " + max + "; thermometer_id = " + thermometer_id + "; threshold_name = " + threshold_name);

        $(this).closest('tr').find('.threshold-trigger-min').text(min);
        $(this).closest('tr').find('.threshold-trigger-max').text(max);

        $(this).closest('li').find('.threshold-trigger .name').val("");
        //$(this).closest('li').find('.trigger-slider').data('slider').value[0] = -1
        //$(this).closest('li').find('.trigger-slider').data('slider').value[1] = 50

        var params = {thermometer_id: thermometer_id, threshold_name: threshold_name, min: min, max: max}

        apiCall('/threshold', 'POST', params, function(data) {

            if (data.ok) {
                $this.closest('table').find('tr:last').after(threshold_template(data.result));

                $this.closest('table').find('tr:last').find('.trigger-slider').slider();
            }
            else {
                notification.error("Failed to add threshold : " + data.result);
            }
        });
    });
}
