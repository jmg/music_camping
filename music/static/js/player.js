$(document).ready(function() {

    var Player = function() {

        var playerEl = $("#player-wrapper");
        var songTitleEl = playerEl.find(".song-title");
        var currentSong = null;

        var _play = function(song) {

            $("#current-song").val(JSON.stringify(song));
            var currentSongEl = $("#song-" + song.id);
            that.activateSong(currentSongEl);

            $.post("/playlist/play/", {"song_id": song.id }, function() {

                songTitleEl.html("Playing: " + song.name);
            });
        }

        this.stop = function() {

            $.post("/playlist/stop/", {}, function() {

                songTitleEl.html("Stopped");
            });
        }

        this.playSong = function(el, e) {

            e.preventDefault();

            var song = $(el).data("song");
            _play(song);
        }

        this.play = function() {

            currentSong = getCurrentSong();
            _play(currentSong);
        }

        this.pause = function() {

            $.post("/playlist/pause/", {}, function() {

                songTitleEl.html("Paused");
            });
        }

        var getCurrentSong = function() {
            return JSON.parse($("#current-song").val());
        }

        var changesong = function(next) {

            currentSong = getCurrentSong();
            var params = {}

            if (next) {
                params.next = true;
            } else {
                params.prev = true;
            }

            $.post("/playlist/changesong/", params, function(song) {

                song = JSON.parse(song);
                _play(song);
            });
        }

        this.next = function() {

            changesong(true);
        }

        this.previous = function() {

            changesong(false);
        }

        this.activateSong = function(currentSongEl) {

            $(".active-song").removeClass("active-song");
            currentSongEl.closest("tr").addClass("active-song");
        }

        var that = this;
    }

    window.player = new Player();
});
