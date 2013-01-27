$(document).ready(function() {
    $('#next').click(function(ev) {
        $('#instructions').attr('src', '/images/buttonrules.png');
        $(this).hide();
    });
    $('#play').click(function(ev) {
        window.location = '/game';
    });
});
