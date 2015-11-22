$(function() {
  var player = videojs('player');
  player.play();
  player.enterFullWindow();
  player.ready(function(){
    $('#status').html('连接成功！');
    $('#resolution').removeClass('hidden');
  });
  setInterval(function() {
    var w = $('#width');
    var h = $('#height');
    w.html(player.videoWidth());
    h.html(player.videoHeight());
  }, 1000);
});