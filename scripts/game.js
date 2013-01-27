var state = 'waiting';
var action = null;
var direction = null;
var initialised = false;
var musicplay = true;
var soundplay = true;
var shifters = $('table.grid td.shifter');
var target = $('<div id="target"/>');
var tiles = $('table.grid td.tile');
var pokedex = {};
var heart = 1;
var hearts = [
    'tiny',
    'small',
    'medium',
    'large'
];
var abilities = [
    'rotate_right',
    'rotate_left',
    'swap_tiles',
    'shift_tiles'
];
var performNoAction = function() {
    performAction({action: 'timeout'});
};
var TIMEOUT = 5000;
var timer = setTimeout(performNoAction, TIMEOUT);

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

var updatePlayer = function(pdata) {
    player.x = pdata.x;
    player.y = pdata.y;
    player.heartbeats = pdata.heartbeats;
    player.heartrate = pdata.heartrate;
    player.abilities = pdata.abilities;
    //Update position
    var tile = getTileElement(player.x, player.y);
    tile.append(player.element);
    player.element.removeClass('happy nervous worried scared terrified');
    if (player.heartrate > 170) {
        player.element.addClass('terrified');
    } else if (player.heartrate > 140) {
        player.element.addClass('scared');
    } else if (player.heartrate > 110) {
        player.element.addClass('worried');
    } else if (player.heartrate > 80) {
        player.element.addClass('nervous');
    } else {
        player.element.addClass('happy');
    }

    //Update abilities
    $.each(player.abilities, function(index, item) {
        var blocker = $('#' + abilities[index] + ' div.blocker');
        if (item !== 0) {
            blocker.show();
        } else {
            blocker.hide();
        }
    });

    //Update heartbeats
    var percent = (player.heartbeats  * 100 / MAX_BEATS);
    $('#bar').css(
        'height', 
        100 - percent + '%'
    );

    //Update heartrate

    //Update active tiles
    tiles.removeClass('active current');
    var curTile = tile;
    var x = player.x;
    var y = player.y;
    curTile.addClass('current');
    for (var i=0; i < 3; i++) {
        if (curTile.hasClass('up')) {
            y = (y - 1) % 10;
        } else if (curTile.hasClass('right')) {
            x = (x + 1) % 10;
        } else if (curTile.hasClass('down')) {
            y = (y + 1) % 10;
        } else {
            x = (x - 1) % 10;
        }
        curTile = getTileElement(x, y);
        curTile.addClass('active');
    }
};

var updateMonsters = function(monsters) {
    $.each(pokedex, function(monster, element) {
        element.detach();
    });
    $.each(monsters, function(monster, position) {
        if (!pokedex.hasOwnProperty(monster)) {
            pokedex[monster] = $('<span class="monster ' + monster + '"/>');
            if(initialised)
                playSound(monster);
        }
        getTileElement(position.x, position.y).append(pokedex[monster]);
    });
    initialised = true;
};

var handleUpdate = function(rsp) {
    clearTimeout(timer);
    if (rsp.hasOwnProperty('world')) {
        updateTiles(rsp.world);
    }
    if (rsp.hasOwnProperty('player')) {
        updatePlayer(rsp.player);
    }
    if (rsp.hasOwnProperty('monsters')) {
        updateMonsters(rsp.monsters);
    }
    if (rsp.hasOwnProperty('is_dead') && rsp.is_dead) {
        $('#overlay').show();
    } else {
        timer = setTimeout(performNoAction, TIMEOUT);
    }
};

var performAction = function(params) {
    $.post(
        'action',
        JSON.stringify(params),
        handleUpdate
    );
};

var audio = $('audio');
var playBeat = function() {
    if(soundplay) {
        audio[0].load();
        audio[0].play();
    }
};
function choice(arr){
    var c = arr.length;
    var f = Math.random();
    var i = Math.floor(c*f);
    return arr[i];
};
var togglemusic = function() {
    if(musicplay) {
        musicplay = false;
        $('#soundtrack1')[0].pause();
        $('#soundtrack2')[0].pause();
        $('#soundtrack3')[0].pause();
        $('#glitch1')[0].pause();
        $('#glitch2')[0].pause();
        $('#glitch3')[0].pause();
        $('#music').removeClass('musicon');
        $('#music').addClass('musicoff');
    }
    else {
        musicplay = true;
        replay_audio();
        $('#music').removeClass('musicoff');
        $('#music').addClass('musicon');
    }
};
var togglesound = function() {
    soundplay = !soundplay;
    $('#sound').removeClass('soundon soundoff');
    $('#sound').addClass(soundplay?'soundon':'soundoff');
};

var replay_audio = function() {
    if(musicplay) {
        var id='#soundtrack'+choice(['2','3']);
        $(id)[0].load();
        $(id)[0].play();
    }
};
var choose_glitch = function(arr) {
    if(musicplay) {
        if(choice([1,2,3])==1) {
            var id='#glitch'+choice(['1','2','3']);
            $(id)[0].load();
            $(id)[0].play();
        }
        else {
            var id='#soundtrack'+choice(arr);
            $(id)[0].load();
            $(id)[0].play();
        }
    }
};
var foley = function(id) {
  if(soundplay) {
    $(id)[0].load();
    $(id)[0].play();
  }
};
var playSound = function(monster) {
        if(monster === 'stove' || monster === 'lighter' || monster === 'flame')
            foley("#fire");
        else if(monster === 'jelly' || monster === 'shark' || monster === 'octo')
            foley('#water');
        else if(monster === 'spider' || monster === 'rat' || monster === 'snake')
            foley('#crawlies');
};
var beat2 = function() {
    playBeat();
    manageBeat();
};
var beat1 = function() {
    playBeat();
    heart += 1;
    $('#heart').removeClass('tiny small medium large').addClass(hearts[heart]);
    setTimeout(beat2, 200);
};
var manageBeat = function() {
    if (player.heartrate > 149) {
        heart = 2;
    } else if (player.heartrate > 99) {
        heart = 1;
    } else {
        heart = 0;
    }
    $('#heart').removeClass('tiny small medium large').addClass(hearts[heart]);
    var time = 60000 / (player.heartrate / 2) - 200;
    time = time < 400 ? 400 : time;
    setTimeout(beat1, time);
};

$(document).ready(function() {
    $('td.tile', 'table.grid').mouseover(function(ev) {
        if (state === 'targeting') {
            $(ev.currentTarget).append(target);
        }
    });
    $('td.tile', 'table.grid').mousemove(function(ev) {
        if (state === 'targeting') {
            target.removeClass('up_cursor down_cursor left_cursor right_cursor horizontal_cursor vertical_cursor');
            if(action === 'shift_tiles' || action === 'swap_tiles'){
                // Do stuff based on the offsetX and offsetY
                if(ev.offsetX>ev.offsetY)
                    if(64-ev.offsetX>ev.offsetY) {
                        target.addClass('up_cursor');
                        direction = 'up';
                    }
                    else {
                        target.addClass('right_cursor');
                        direction = 'right';
                    }
                else
                    if(64-ev.offsetX>ev.offsetY) {
                        target.addClass('left_cursor');
                        direction = 'left';
                    }
                    else {
                        target.addClass('down_cursor');
                        direction = 'down';
                    }
            }
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
    var swap_tiles = function() {
        return function(ev) {
            state = 'targeting';
            action = 'swap_tiles';
            target.addClass('swap_tiles');
            ev.stopPropagation();
         };
    };
    var shift_tiles = function(){
        return function(ev) {
            state = 'targeting';
            action = 'shift_tiles';
            target.addClass('shift_tiles');
            ev.stopPropagation();
         };
    };
    $('#rotate_right').click(rotateFn('rotate_right'));
    $('#rotate_left').click(rotateFn('rotate_left'));
    $('#swap_tiles').click(swap_tiles());
    $('#shift_tiles').click(shift_tiles());
    $('body').click(function(ev) {
        if (state !== 'waiting') {
            action = null;
            state = 'waiting';
            target.detach();
        }
    });
    $('body').keypress(function(ev) {
        switch(ev.keyCode){
        case 113:
        case 81:
            state = 'targeting';
            action = 'rotate_left';
            target.removeClass('rotate_right rotate_left');
            target.addClass('rotate_left');
            break;
        case 119:
        case 87:
            state = 'targeting';
            action = 'rotate_right';
            target.removeClass('rotate_right rotate_left');
            target.addClass('rotate_right');
            break;
        case 101:
        case 69:
            state = 'targeting';
            action = 'swap_tiles';
            target.addClass('swap_tiles');
            break;
        case 114:
        case 82:
            state = 'targeting';
            action = 'shift_tiles';
            target.addClass('shift_tiles');
            break;
        }
    });
    tiles.click(function(ev) {
        console.log(action);
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
        else if (action === 'swap_tiles'|| action === 'shift_tiles') {
            var tile = $(ev.currentTarget);
            var x = tile.prevAll().length - 1;
            var y = tile.parent().prevAll().length -1;
            target.removeClass('up_cursor down_cursor left_cursor right_cursor horizontal_cursor vertical_cursor');
            target.detach();
            performAction({action: action, x: x, y: y,direction:direction});
            action = null;
            direction = null;
            state = 'waiting';
        }
        ev.stopPropagation();
    });
    $('div.blocker').click(function(ev) {
        ev.stopPropagation();
    });
    $('#overlay').click(function(ev) {
        ev.stopPropagation();
    });
    $('#gameover input').click(function(ev) {
        window.location = '/results';
    });
    updatePlayer(player);
    updateMonsters(starting_monsters);
    manageBeat();
});
