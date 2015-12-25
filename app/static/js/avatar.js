/**
 * Created by rsj217 on 14-12-12.
 */


var MAXWIDTH = 500;
var MAXHEIGHT = 500;
var JCROPRATIO = 1;

jQuery(function($){

  var jcrop_api, boundx, boundy;
  FileReader = window.FileReader;

  $("#avatar-file").change(function(){

    var image = document.createElement('img');

    $('#avatar-wrapper').css({
      'max-width': MAXWIDTH,
      'max-height': MAXHEIGHT,
      'width': MAXWIDTH,
      'height': MAXHEIGHT
    }).addClass('avatar-wrapper');
    $('#preview-wrapper').addClass('preview-wrapper');

    if(jcrop_api != null){
      jcrop_api.destroy();
    }

    if(FileReader){

      var reader = new FileReader();
      var file = this.files[0];
      reader.readAsDataURL(file);

      reader.onload = function(e){

        image.src = this.result;
        image.id = "avatar";
        // 显示图片
        $("#preview").attr("src", this.result).css('display', 'block');

        // 设置长宽比,延迟0.4秒
        setTimeout(function(){
          // 获取图片真实宽高
          var width = image.width;
          var height = image.height;
          var rat;
          // 设置图片显示宽高
          if(width > MAXWIDTH){
            rat = MAXWIDTH / width;
            width = MAXWIDTH;
            height = height * rat;
          }
          if(height > MAXHEIGHT){
            rat = MAXHEIGHT / height;
            height = MAXHEIGHT;
            width = width * rat;
          }
          // 更新显示图片的宽高
          image.width = width;
          image.height = height;
          // 增加显示图片到 dom
          $("#avatar-wrapper").html(image);
          // 修改预览图片宽高
/*          $("#preview").css({
            width: width,
            height: height
          });*/

          $(image).Jcrop({
            aspectRatio: JCROPRATIO,
            onChange: updatePreview,
            onChange: updateCoords,
            onSelect: updateCoords,
            onSelect: updatePreview,
            onRelease: clearCoords
          },function(){
            jcrop_api = this;
          });
        }, 500); //设定时间延迟结束
      };
    }
  });
});

function updatePreview(c){
  if( parseInt(c.w)> 0){
    boundx = $("#avatar").width();
    boundy = $("#avatar").height();
    if (parseInt(c.w) > 0){
      var rx = 150 / c.w;
      var ry = 150 / c.h;
      $("#preview").css({
        width: Math.round(rx * boundx) + 'px',
        height: Math.round(ry * boundy) + 'px',
        marginLeft: '-' + Math.round(rx * c.x) + 'px',
        marginTop: '-' + Math.round(ry * c.y) + 'px'
      });
    }
  }
};

function clearCoords(){
  $('#x1').val("");
  $('#y1').val("");
  $('#x2').val("");
  $('#y2').val("");
  $('#w').val("");
  $('#h').val("");
};

function updateCoords(c){
  $('#x1').val(Math.round(c.x));
  $('#y1').val(Math.round(c.y));
  $('#x2').val(Math.round(c.x2));
  $('#y2').val(Math.round(c.y2));
  $('#w').val(Math.round(c.w));
  $('#h').val(Math.round(c.h));
};



function allowed_extensions(type){
  pattern = /(^image\/png$)|(^image\/jpg$)|(^image\/jpeg$)/i;
  return pattern.test(type);
}
