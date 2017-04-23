from os import listdir

dirname = 'newsCraw/modules/'

__all__ = [ f[:-3] for f in listdir(dirname) if f[-3:] == '.py' and f[:-3] != '__init__']