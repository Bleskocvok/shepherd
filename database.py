
import os
import ast

class Database:
    def __init__(self, folder):
        self.channels = {}
        self.folder = folder
        # create folder if it doesn't exist
        if not os.path.isdir(folder):
            os.mkdir(folder)
        # load channels and user data
        self.channels = self.load('channels.txt')
        self.users = self.load('users.txt')

    def get_channels(self):
        return self.channels

    def remove_channel(self, ID : int):
        self.channels.pop(ID)
        self.save(self.channels, 'channels.txt')

    def set_channel(self, ID : int, time : (int, int)):
        self.channels[ID] = time
        self.save(self.channels, 'channels.txt')

    def get_user_stats(self, ID):
        return self.users.get(ID, [])

    def add_user_stats(self, ID, value):
        self.users.setdefault(ID, []).append(value)
        self.save(self.users, 'users.txt')

    def edit_last_stats(self, ID, value):
        stats = self.get_user_stats(ID)
        if len() > 0:
            stats[-1] = value

    def save(self, struct, fname):
        with open(self.folder + "/" + fname, 'w') as f:
            f.write(str(struct))

    def load(self, fname):
        self.ensure_file(fname)
        with open(self.folder + '/' + fname) as f:
            return ast.literal_eval(f.read())

    def ensure_file(self, fname):
        '''Creates file if it doesn\'t exist'''
        fname = self.folder + "/" + fname
        if not os.path.isfile(fname):
            with open(fname, 'w') as f:
                f.write('{}') 
