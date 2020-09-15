$(document).ready(function(){
  var c_time=current_time(new Date());
  var hr=parseInt(c_time.split(':')[0]);
  var min=parseInt(c_time.split(':')[1]);
  $('.tp-min>span').html(min < 10 ? '0' + min : min);
  $('.tp-hr>span').html(hr);
  $('.tp-hr>.tp-down-arrow').on('mousedown touchstart', function(){
    change_hr(-1);
    var counter = 0;
    decrement = setInterval(function(){
      if (counter > 1) {
        change_hr(-1);
      }
      counter++;
    }, 100);
  }).bind('mouseup mouseleave touchend', function(){
    clearInterval(decrement);
  });
  $('.tp-min>.tp-down-arrow').on('mousedown touchstart', function(){
    change_min(-1);
    var counter = 0;
    increment = setInterval(function(){
      if (counter > 1) {
        change_min(-1);
      }
      counter++;
    }, 100);
  }).bind('mouseup mouseleave touchend', function(){
    clearInterval(increment);
  });
  $('.tp-hr>.tp-up-arrow').on('mousedown touchstart', function(){
    change_hr(1);
    var counter = 0;
    increment = setInterval(function(){
      if (counter > 1) {
        change_hr(1);
      }
      counter++;
    }, 100);
  }).bind('mouseup mouseleave touchend', function(){
    clearInterval(increment);
  });
  $('.tp-min>.tp-up-arrow').on('mousedown touchstart', function(){
    change_min(1);
    var counter = 0;
    increment = setInterval(function(){
      if (counter > 1) {
        change_min(1);
      }
      counter++;
    }, 100);
  }).bind('mouseup mouseleave touchend', function(){
    clearInterval(increment);
  });
});

function change_hr(offset) {
  var hr = parseInt($('.tp-hr>span').html());
  hr = hr + offset;
  if (hr < 0) {
    hr = 23;
  } else if (hr > 23) {
    hr = 0;
  }
  $('.tp-hr>span').html(hr < 10 ? '0' + hr : hr);
}

function change_min(offset) {
  var min = parseInt($('.tp-min>span').html());
  min = min + offset;
  if (min < 0) {
    min = 59;
  } else if (min > 59) {
    min = 0;
  }
  $('.tp-min>span').html(min < 10 ? '0' +min : min);
}

function current_time(date) {
  var hours = date.getHours();
  var minutes = date.getMinutes();
  minutes = minutes < 10 ? '0' + minutes : minutes;
  return (hours + ':' + minutes + ':');
}