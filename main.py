import wx
import json
from modules.MainWindow import *

def read_config():
    with open('./data/config.json', 'r') as f:
        return json.load(f)


def init_app():
    config = read_config()

    if config is None:
        print('No config.json file found')
        exit()

    title = config['name'] + ' ' + config['version']
    size = (config["defaultSize"]['width'], config["defaultSize"]['height'])

    app = wx.App(False)
    mainFrame = MainWindow(None, title=title, size=size, config=config)
    app.SetTopWindow(mainFrame)
    app.MainLoop()


if __name__ == '__main__' :
    init_app()
