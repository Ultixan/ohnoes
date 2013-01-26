var MAX_BEATS = 1000;

var state = 'waiting';
var action = null;
var shifters = $('table.grid td.shifter');
var target = $('<div id="target"/>');
var tiles = $('table.grid td.tile');

var world = {
  player: {
    element: $('<span id="player"/>'),
    heartBeats: 400,
    heartRate: 80,
    x: 0,
    y: 0,
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
    var row = $('table.grid tr:nth-child(' + (y + 2) + ')');
    var elem = $('td:nth-child(' + (x + 2) + ')', row);
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

var updatePlayer = function(player) {
    //Update position
    var tile = getTileElement(player.x, player.y);
    tile.append(world.player.element);

    //Update abilities

    //Update heartbeats
    var percent = (world.player.heartBeats  * 100 / MAX_BEATS);
    $('#bar').css(
        'height', 
        100 - percent + '%'
    );

    //Update heartrate
};

var handleUpdate = function(rsp) {
    if (rsp.hasOwnProperty('world')) {
        updateTiles(rsp.world);
    }
};

var performAction = function(params) {
    $.post(
        'action',
        JSON.stringify(params),
        handleUpdate
    );
};

$(document).ready(function() {
    $('td.tile', 'table.grid').mouseover(function(ev) {
        if (state === 'targeting') {
            $(ev.currentTarget).append(target);
        }
    });
    var rotateFn = function(name) {
        return function(ev) {
            state = 'targeting';
            action = name;
            target.removeClass('rotate_right rotate_left');
            target.addClass(name);
            ev.stopPropagation();
        };
    };
    $('#rotate_right').click(rotateFn('rotate_right'));
    $('#rotate_left').click(rotateFn('rotate_left'));
    $('body').click(function(ev) {
        if (state !== 'waiting') {
            action = null;
            state = 'waiting';
            target.detach();
        }
    });
    tiles.click(function(ev) {
        if (action === 'rotate_left' || action === 'rotate_right') {
            var tile = $(ev.currentTarget);
            var x = tile.prevAll().length - 1;
            var y = tile.parent().prevAll().length - 1;
            target.removeClass('rotate_right rotate_left');
            target.detach();
            performAction({action: action, x: x, y: y});
            action = null;
            state = 'waiting';
        }
        ev.stopPropagation();
    });
});
