/* Handlebars */
loadTemplate = function(template_id) {
    var source = $(template_id).html();
    return Handlebars.compile(source);
}

/* API related */
var apiCall = function(path, method, data, callback) {
	$.ajax({
	  url: path,
	  type: method,
	  async: true,
	  dataType: "json",
	  data: JSON.stringify(data),
	  contentType: 'application/json;charset=UTF-8',
	  success: callback
	});
};

/* Notification zone */
notification = {
    show: function(cls, msg) {
        msg = msg.replace(/\n/g,'<br/>').replace(/ /g, '&nbsp;');
        console.log(msg);
        $('#notification-bar').attr('class', cls).stop().html(msg).show().fadeIn(500).delay(2000).fadeOut(500);
    },
    error: function(msg) {
        this.show('error', msg);
    },
    warning: function(msg) {
        this.show('warning', msg);
    },
    info: function(msg) {
        this.show('info', msg);
    },
    success: function(msg) {
        this.show('success', msg);
    }
}