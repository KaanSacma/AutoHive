import os
import wx
from modules.Handler import *

class MainWindow(wx.Frame):
    def __init__(self, parent, title, size, config):
        wx.Frame.__init__(self, parent, title=title, size=size)

        self.dirname = ''
        self.filename = ''
        self.config = config
        self.keys = self.config['keys']
        self.handler = Handler()

        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        font_info = self.config['font']
        wx.Font.AddPrivateFont(font_info["path"] + font_info["name"] + "." + font_info["fileType"])
        font = wx.Font(font_info["size"], wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=font_info["name"])
        self.control.SetFont(font)

        self.SetTopBar()
        self.CreateStatusBar(style=wx.STB_SHOW_TIPS)

        self.control.Bind(wx.EVT_KEY_DOWN, self.OnKey)

        bgcolor = self.config["backgroundColor"]
        fgcolor = self.config["foregroundColor"]
        backgroundColor = wx.Colour(bgcolor["R"], bgcolor["G"], bgcolor["B"])
        foregroundColor = wx.Colour(fgcolor["R"], fgcolor["G"], fgcolor["B"])
        self.control.SetForegroundColour(foregroundColor)
        self.control.SetBackgroundColour(backgroundColor)

        self.Center()
        self.Show(True)

    def OnKey(self, event):
        key = event.KeyCode
        if event.ControlDown():
            self.OnCtrlKey(key)
        event.Skip()

    def OnCtrlKey(self, key):
        char = chr(key)
        if char == self.keys["save"]:
            self.OnSave(None)
        elif char == self.keys["open"]:
            self.OnOpen(None)
        elif char == self.keys["run"]:
            self.OnRun(None)

    def OnOpen(self, e):
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.AH", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r+')
            self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()

    def OnSave(self, e):
        try:
            f = open(os.path.join(self.dirname, self.filename), 'w', encoding='utf8')
            f.write(self.control.GetValue())
            f.close()
        except:
            try:
                dlg = wx.FileDialog(self, "Save to file:", ".", "", "*.AH", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if dlg.ShowModal() == wx.ID_OK:
                    self.filename = dlg.GetFilename()
                    self.dirname = dlg.GetDirectory()
                    f = open(os.path.join(self.dirname, self.filename), 'w', encoding='utf8')
                    f.write(self.control.GetValue())
                    f.close()
                dlg.Destroy()
            except:
                pass

    def OnSaveAs(self, event):
        try:
            dlg = wx.FileDialog(self, "Save to file:", ".", "", "*.AH", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetFilename()
                self.dirname = dlg.GetDirectory()
                f = open(os.path.join(self.dirname, self.filename), 'w', encoding='utf8')
                f.write(self.control.GetValue())
                f.close()
            dlg.Destroy()
        except:
            pass

    def OnRun(self, e):
        self.handler.Parse(self.control.GetValue())

    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, self.config["description"], "About " + self.config["name"], wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)

    def SetTopBar(self):
        file_menu = wx.Menu()
        menu_openfile = file_menu.Append(wx.ID_OPEN, 'Open', " Open a file (CTRL+" + self.keys["open"] + ")")
        menu_savefile = file_menu.Append(wx.ID_SAVE, 'Save', " Save a file (CTRL+" + self.keys["save"] + ")")
        menu_savefileas = file_menu.Append(wx.ID_SAVEAS, 'Save as', " Save as")
        menu_exit = file_menu.Append(wx.ID_EXIT, "Exit", " Exit the app (ALT+F4)")

        help_menu = wx.Menu()
        menu_about = help_menu.Append(wx.ID_ABOUT, "About", " About this app")

        action_menu = wx.Menu()
        menu_run = action_menu.Append(wx.ID_ANY, "Run", " Run the script (CTRL+" + self.keys["run"] + ")")

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "File")
        menu_bar.Append(help_menu, "Help")
        menu_bar.Append(action_menu, "Action")
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.OnOpen, menu_openfile)
        self.Bind(wx.EVT_MENU, self.OnSave, menu_savefile)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menu_savefileas)
        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menu_about)
        self.Bind(wx.EVT_MENU, self.OnRun, menu_run)
