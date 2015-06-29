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

    $('#play-music').ajaxForm({
        url: '/player', type: 'post',dataType:  'json',
        success : function(data){
           if (data.ok == "false") {
            $('#pausing').attr('src',"../static/img/player_play.png");
            $('#song_text').text("");
            notification.error(data.name);
           }
          else {
            $('#pausing').attr('src',"../static/img/player_pause.png");
            $('#song_text').text("----- " + data.name + " -----");
            $('#tag_text').text("Catégorie "+ data.tags);
          }
          }
        } );


  $('#pausing').click(function(){
      $.ajax({
      url: '/player/pause',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify("data"),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
          if (data.ok == "true") {
            $('#pausing').attr('src',data.src);
          }
          else {
            notification.error(data.src);
          }
        }
    });
    });

    $('#next').click(function(){
      $.ajax({
      url: '/player/next',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify("data"),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
          if (data.ok == true){
            $('#song_text').text(data.name);    
          }
          else {
            notification.error(data.name)
          }
        }
    });
    });

  $('#previous').click(function(){
      $.ajax({
      url: '/player/previous',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify("data"),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
          if (data.ok == true){
            $('#song_text').text(data.name);    
          }
          else {
            notification.error(data.name)
          }
        }
    });
    });


});


  function on_tag_click(this_button){
      $.ajax({
      url: '/player/tags',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify(this_button),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
        if (data.ok == true){
            $('#pausing').attr('src',"../static/img/player_pause.png");
            $('#song_text').text("----- " + data.name + " -----");
            $('#tag_text').text("Catégorie "+ data.tags);
          }
          else {
            $('#pausing').attr('src',"../static/img/player_play.png");
            $('#song_text').text("");
            notification.error(data.name);
           }
        }
    });
    };