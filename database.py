
class Database:
    def __init__(self):
        self.channels = {}

    def get_channels(self):
        return self.channels

    def remove_channel(self, ID : int):
        self.channels.pop(ID)

    def set_channel(self, ID : int, time : (int, int)):
        self.channels[ID] = time

    def get_user_stats(self, user):
        pass

    def get_channel_stats(self, channel):
        pass

