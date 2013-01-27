$(document).ready(function() {
    var target = 'explode';
    var scores = {
        '#turns': {
            value: turns,
            score: turns * 20
        },
        '#beats': {
            value: heartbeat,
            score: heartbeat * -1
        },
        '#rate': {
            value: heartrate,
            score: (heartrate - 50) * -3
        }
    };
    if (monster) {
        $('#monster_hook').text(monster);
        target = 'killed';
    } else if (heartrate < 200 && heartbeat <= 0) {
        target = 'survivor';
    }

    $('.' + target).show();
    $('#image').addClass(target);

    var total = 0;
    $.each(scores, function(key, score) {
        var row = $(key);
        $('.value', row).text(score.value);
        $('.score', row).text(score.score);
        total += score.score;
    });
    $('#total .score').text(total);
});
