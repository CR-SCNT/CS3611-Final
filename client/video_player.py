import vlc, os, queue, threading


class Player:
    '''
    '''
    def __init__(self, msize):
        self.instance = vlc.Instance("--network-caching=600")
        self.medialist = self.instance.media_list_new()
        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_media_list(self.medialist)
        self.list_player.set_playback_mode(vlc.PlaybackMode.loop)
        self.playlist = queue.Queue(maxsize=msize)
        self.activicated = False
        self.player_thread = threading.Thread(target=self.player_manager, daemon=True)
        self.player_thread.start()

    def player_manager(self):
        while True:
            try:
                segment_path = self.playlist.get(timeout=1)
                media = self.instance.media_new(segment_path)
                self.medialist.add_media(media)
                if not self.activicated:
                    self.activicated = True
                    self.list_player.play()
            except queue.Empty:
                continue
            except Exception as e:
                print(e)

    def add_playlist(self, path):
        if not os.path.exists(path):
            return False
        else:
            self.playlist.put(path, block=False)

    def stop(self):
        if self.list_player:
            self.list_player.stop()
            self.activicated = False

'''
if "__main__" == __name__:
    player = Player()
'''