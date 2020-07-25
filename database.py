
import os
import ast

class Database:
    def __init__(self, folder):
        self.channels = {}
        self.folder = folder
        # create folder if it doesn't exist
        if not os.path.isdir(folder):
            os.mkdir(folder)
        # load channels
        self.ensure_file('channels.txt')
        with open(folder + '/channels.txt') as file:
            self.channels = ast.literal_eval(file.read())

    def get_channels(self):
        return self.channels

    def remove_channel(self, ID : int):
        self.channels.pop(ID)
        self.save(self.channels, 'channels.txt')

    def set_channel(self, ID : int, time : (int, int)):
        self.channels[ID] = time
        self.save(self.channels, 'channels.txt')

    def get_user_stats(self, user):
        pass

    def get_channel_stats(self, channel):
        pass

    def save(self, struct, fname):
        with open(self.folder + "/" + fname, 'w') as f:
            f.write(str(struct))

    def ensure_file(self, fname):
        '''Creates file if it doesn\'t exist'''
        fname = self.folder + "/" + fname
        if not os.path.isfile(fname):
            with open(fname, 'w') as f:
                f.write('{}') 
