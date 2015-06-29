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
              window.history.back();
              return;
            }
        }

  });

    $('.addCategory').click(showHiddenArticles);
    $('.hideCategory').click(hideHiddenArticles);
});

function showHiddenArticles() {
    var category = $(this).data('category');
    var $categ = $(this).closest(".category-wrapper");
    $categ.find(".article.more").css('display', 'inline-block');

    $categ.find(".addCategory").hide();
    $categ.find(".hideCategory").show();
}

function hideHiddenArticles() {
    var category = $(this).data('category');
    var $categ = $(this).closest(".category-wrapper");
    $categ.find(".article.more").hide();

    $categ.find(".addCategory").show();
    $categ.find(".hideCategory").hide();
}
