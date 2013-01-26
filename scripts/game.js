var world = {
  player: {
    heartBeats: 1000,
    heartRate: 80,
    position: {
      x: 0,
      y: 0
    },
    abilities: {
      turnLeft: true,
      turnRight: true,
      shiftTiles: true,
      swapTiles: true,
      blankie: false,
      bear: false,
      light: false,
      rattle: false,
      pacifier: false,
      duckie: false
    }
  }
};

var getTileElement = function(x, y) {
    var row = $('table.grid tr:nth-child(' + (y + 1) + ')');
    var elem = $('td:nth-child(' + (x + 1) + ')', row);
    return elem;
};

var updateTiles = (function() {
  var _updateTile = function(tile) {
    var elem = getTileElement(tile.x, tile.y);
    elem.removeClass('up right down left');
    elem.addClass(tile.direction);
  };
  return function(tiles) {
    $.each(tiles, function(index, tile) {
      _updateTile(tile);
    });
  };
})();

$(document).ready(function() {
  
});
