$(document).ready(function() {
    var clickFn;
    var click2 = function(ev) {
        $('#instructions').attr('src', '/images/buttonrules.png');
        $('#next').hide();
    };
    var click1 = function(ev) {
        $('#instructions').attr('src', '/images/items.png');
        clickFn = click2;
    };
    clickFn = click1;
    $('#next').click(function(ev) {
        clickFn(ev);
    });
    $('#play').click(function(ev) {
        window.location = '/game';
    });
});
