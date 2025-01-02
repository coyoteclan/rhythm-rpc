from gi.repository import GObject, RB, Peas, GLib

import threading
from thirdparty.discordrpc import RPC
from thirdparty.discordrpc.utils import timestamp


class RhythmRPC(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)
    
    def __init__(self):
        super(RhythmRPC, self).__init__()
        self.shell = None
        self.player = None
        self.rpc_thread = None
        self.rpc_running = False
    
    def do_activate(self):
        print("Activated")
        
        self.shell = self.object
        self.player = self.shell.props.shell_player
        self.player.connect("playing-changed", self.onPlayerStatusChanged)
        
        try:
            self.rpc = RPC(app_id=1321109979880624270)
            
            self.rpc.set_activity(
                state="No Song",
                large_image="org_gnome_rhythmbox3",
                large_text="Rhythmbox",
                ts_start=timestamp,
                ts_end=1752426021
            )
            
            self.rpc_running = True
            self.rpc_thread = threading.Thread(target=self.run_rpc)
            self.rpc_thread.daemon = True
            self.rpc_thread.start()
            
            
        except ConnectionRefusedError:
            print("Rhythm-RPC: Connection Refused")
        except ConnectionAbortedError:
            print("Rhythm-RPC: Connection Aborted")
        except ConnectionResetError:
            print("Rhythm-RPC: Connection Reset")
    
    def onPlayerStatusChanged(self, player, playing):
        _song = self.player.get_playing_entry()
        _nosong = None
        if not _song:
            _nosong = True
        else:
            _nosong = False
        
        title = _song.get_string(RB.RhythmDBPropType.TITLE)
        artist = _song.get_string(RB.RhythmDBPropType.ARTIST)
        
        print(title, artist)
        self.updateDiscordStatus(playing=playing, song=title, artist=artist, noSong=_nosong)
    
    def updateDiscordStatus(self, playing, song, artist, noSong=False):
        if noSong:
            self.rpc.set_activity(
                state="No Song",
                large_image="org_gnome_rhythmbox3",
                large_text="Rhythmbox",
                ts_start=timestamp,
                ts_end=1752426021
            )
            return
        elif playing:
            self.rpc.set_activity(
                state=f"by {artist}",
                details=song,
                large_image="org_gnome_rhythmbox3",
                large_text="Listening to music on Rhythmbox",
                small_image="play",
                small_text="Playing",
                ts_start=timestamp,
                ts_end=1752426021
            )
            return
        elif not playing:
            self.rpc.set_activity(
                state=f"by {artist}",
                details=song,
                large_image="org_gnome_rhythmbox3",
                large_text="Listening to music on Rhythmbox",
                small_image="pause",
                small_text="Paused",
                ts_start=timestamp,
                ts_end=1752426021
            )
            return
    
    def run_rpc(self):
        try:
            self.rpc.run()
        except Exception as e:
            print(f"Rhythm-RPC: Error {e}")
    
    def do_deactivate(self):
        print("Deactivated")
        self.shell = None
        self.player = None
        
        if self.rpc_running:
            self.rpc_running = False
            if self.rpc_thread and self.rpc_thread.is_alive():
                self.rpc_thread.join(timeout=2.0)
                self.rpc_thread = None
        if self.rpc:
            try:
                self.rpc.disconnect()
            except Exception as e:
                print(f"Rhythm-RPC: Error {e}")
            finally:
                del self.rpc
