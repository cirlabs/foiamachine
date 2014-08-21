(function() {
  var $point_arr, $points, $progress, activate, active, max, tracker, val;

  $points = $('.progress-points').first();

  $point_arr = $('[data-point]');

  $progress = $('.progress').first();

  val = parseInt($points.data('current')) - 1;

  max = $point_arr.length - 1;

  tracker = active = 0;
  
  activate = function(index) {
    if (index !== active) {
      active = index;
      $point_arr.slice(0, index).addClass('completed');
      $point_arr.eq(active).addClass('active');
      return $progress.css('width', (index / max * 100) + "%");
    }
  };

  $points.on('click', 'li', function(event) {
    var _index;
    _index = $point_arr.index(this);
    tracker = _index === 0 ? 1 : _index === val ? 0 : tracker;
    return activate(_index);
  });

  setTimeout((function() {
    return activate(val);
  }), 1000);

}).call(this);
