$(document).ready(function() {

    var Player = function() {

        var playerEl = $("#player-wrapper");
        var songTitleEl = playerEl.find(".song-title");

        var a = audiojs.createAll({
            trackEnded: function() {
                that.next();
            }
        });

        var audio = a[0];

        var setSong = function(song) {

            $("#current-song").val(JSON.stringify(song));

            audio.load(song.uri);
            audio.play();
            songTitleEl.html(song.name);
        }

        this.stop = function() {

            audio.stop();
        }

        this.playSong = function(el, e) {

            e.preventDefault();

            var song = $(el).data("song");
            setSong(song);
        }

        this.play = function() {

            var currentSong = getCurrentSong();
            setSong(currentSong);
        }

        var getCurrentSong = function() {
            return JSON.parse($("#current-song").val());
        }

        var changesong = function(next) {

            var currentSong = getCurrentSong();
            var params = {}

            if (next) {
                params.next = true;
            } else {
                params.prev = true;
            }

            $.post("/playlist/changesong/", params, function(song) {

                song = JSON.parse(song);
                setSong(song);
                that.play();
            });
        }

        this.next = function() {

            changesong(true);
        }

        this.previous = function() {

            changesong(false);
        }

        var that = this;
    }

    window.player = new Player();
});
