$(document).ready(function() {

      var firstValidFrame = null
    changed=false;
    Leap.loop(function(frame) { 

       if (frame.valid) {
          if (!firstValidFrame) firstValidFrame = frame
          var t = firstValidFrame.translation(frame)

            //assign rotation coordinates
            transX = t[0]
            transY = t[1]
            if (transX > 200 && changed == false){
              console.log("haha")
              changed = true;
              window.location.replace("../");
              return;
            }
        }

  });

    connection_template = loadTemplate('#connection-template');
    alarm_template = loadTemplate('#alarm-template');

    Handlebars.registerPartial("connection-template", $("#connection-template").html());

    Handlebars.registerHelper("hours_real",function(minutes){
      return Math.floor(minutes/60) + ":" + parseInt(FormatNumberLength(minutes%60,2));
    });

    Handlebars.registerHelper("day_str", function(days){
      var str ="";
      for (var i = 0; i < days.length; i++) {
        str += dico_days[days[i]] + " "
      }
      return str
    })
    updateAlarms();
    bindAlarms();



  $('#alarm_creator').on('click',function(data){
    $('#id_alarm_validator_div').attr('style',"display:block");
  });

  $('#hours_down').on('click', function(data){
    if( parseInt($('#hours').val()) >0){
      $('#hours').attr2('value',parseInt($('#hours').val())-1);
    }
    else{
      $('#hours').attr2('value',23);
    }
  });  

  $('#hours_up').on('click', function(data){
    if( parseInt($('#hours').val()) <24){
      $('#hours').attr2('value',parseInt($('#hours').val())+1);
    }
    else {
      $('#hours').attr2('value',0);
    }
  });

  $('#minutes_down').on('click', function(data){
    if( parseInt($('#minutes').val()) >0){
      $('#minutes').attr2('value',parseInt($('#minutes').val())-1);
    }
    else {
      $('#minutes').attr2('value',23);
    }
  });

  $('#minutes_up').on('click', function(data){
    if( parseInt($('#minutes').val()) <59){
      $('#minutes').attr2('value',parseInt($('#minutes').val())+1);
    }
    else {
      $('#minutes').attr2('value',0);
    }

  })

    $('#clock_form').ajaxForm({
        url: '/calendar/create', type: 'post',dataType:  'json',
        success : function(data){
          updateAlarms();
          }
        } );


})

var dico_days = new Array();
  dico_days[0] = "Mon";
  dico_days[1] = "tue"; 
  dico_days[2] = "wed";
  dico_days[3] = "thu"; 
  dico_days[4] = "fri";
  dico_days[5] = "sat"; 
  dico_days[6] = "sun"; 


var updateAlarms = function() {
    $.getJSON('/alarms', function(data) {
            $('.alarm').html('');
            $.each(data.result, function(i, s) {
                $('.select_alarm_area').append(alarm_template(s));
            });
    });
};


var bindAlarms = function() {

    // Expanding a sensor's view (by clicking on its heading)
    $('.select_alarm_area').on('click', ' .heading', function(e) {
      $li = $(this).closest('li');
      $('.alarm li').not($li).find('.details').hide(200);
      $li.find('.details').stop();
      $li.find('.details').toggle(400);
      $('#hours').attr2('value', Math.floor($(this).attr("alarm_minutes")/60));
      $('#minutes').attr2('value',$(this).attr("alarm_minutes")%60);
    }); 

    // Deleting a sensor
    $('.select_alarm_area').on('click', '.heading .delete', function(e) {
        $this = $(this).closest('li');
        var alarm_name = $this.attr('alarm_name');

        apiCall('/alarm/' + alarm_name, 'DELETE', {}, function(data) {
            $this.hide(200, function() {
                $this.remove();
            });
        });

        // Avoid triggering an event on the parent li
        e.stopPropagation();
    });

    // Deleting an event binding
    $('.select_alarm_area').on('click', '.event-connection .delete', function(e) {
        var connection_li = $(this).closest('.event-connection');
        var connection_id = connection_li.attr('data-connection-id');

        apiCall('/connection/' + connection_id, 'DELETE', {}, function(data) {
            if (data.ok) {
                connection_li.hide(300, function() { connection_li.remove(); });
                drawGraph();
            }
        });
    });

    // Adding an event binding
    $('.select_alarm_area').on('click', '.callback-binding .add', function(e) {
        var $this = $(this);
        var cb_form = $this.closest('.callback-binding');

        var event = cb_form.find('input[name="event"]').val();
        var actuator = cb_form.find('select[name="actuator"]').val();
        var callback = cb_form.find('select[name="callback"]:enabled').val();
        //alert(event);
        var params = {event: event, actuator: actuator, callback: callback};


        apiCall('/clockConnection', 'POST', params, function(data) {

            if (data.ok) {
                $this.closest('table').find('tr:last').before(connection_template(data.result));
            }
            else {
                notification.error("Couldn't add a binding between '" + event + "' and '"
                                    + actuator + '.' + callback + "' : " + data.result);
            }
        });

    });

    // Activating the right callbacks' list
    $('.select_alarm_area').on('change', 'select[name="actuator"]', function(e) {
        $('select[name="callback"]').prop('disabled', true);
        $('select[name="callback"][data-actuator-id="' + $(this).val() + '"]').prop('disabled', false);
    });

    // s = $('select[name="callback"][data-actuator-id="889977"]')


    $('.select_alarm_area').on('slideStop', '.trigger-slider.modify', function(ev){
        var $this = $(this);
        var min = $this.data('slider').value[0];
        var max = $this.data('slider').value[1];
        console.log('min = ' + min + '; max = ' + max);
        $(this).parent().parent().find('.trigger-threshold-min').val($(this).val());
    });


    $('.select_alarm_area').on('slideStop', '.trigger-slider.new', function(ev){
        var $this = $(this);
        var min = $this.data('slider').value[0];
        var max = $this.data('slider').value[1];
        console.log('min = ' + min + '; max = ' + max);
        $(this).parent().parent().find('.trigger-threshold-min').val($(this).val());
    });


}

function FormatNumberLength(num, length) {
    var r = "" + num;
    while (r.length < length) {
        r = "0" + r;
    }
    return r;
}
