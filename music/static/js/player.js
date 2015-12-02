$(document).ready(function() {

    var Player = function() {

        var playerEl = $("#player-wrapper");

        var a = audiojs.createAll({
            trackEnded: function() {

            }
        });

        var audio = a[0];

        this.playSong = function(anchor, e) {

            e.preventDefault();
            audio.load($(anchor).attr('data-src'));
            audio.play();

            playerEl.find(".song-title").html($(anchor).text());
        }
    }

    window.player = new Player();
});
