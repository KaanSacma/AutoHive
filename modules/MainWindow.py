import os
import wx
import keyboard
import threading
from modules.Handler import *

def check_key(keys, pressed_key, ctrl_pressed):
    for action, key_info in keys.items():
        if key_info["key"].lower() == pressed_key.lower() and key_info["ctrl"] == ctrl_pressed:
            return action
    return None

class MainWindow(wx.Frame):
    def __init__(self, parent, title, size, config):
        wx.Frame.__init__(self, parent, title=title, size=size)

        self.dirname = ''
        self.filename = ''
        self.config = config
        self.keys = self.config['keys']
        self.handler = Handler()
        keyboard.add_hotkey(self.keys["stop"]["key"], self.OnStopScript, args=(None,))
        keyboard.add_hotkey(self.keys["pause"]["key"], self.OnPauseScript, args=(None,))

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
        char = chr(key)
        action = check_key(self.keys, char, event.ControlDown())

        if action:
            if action == "save":
                self.OnSave(None)
            elif action == "open":
                self.OnOpen(None)
            elif action == "run":
                self.OnRun(None)
            elif action == "stop":
                self.OnStopScript(None)
            elif action == "pause":
                self.OnPauseScript(None)
        event.Skip()

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
        if self.handler.running:
            wx.MessageDialog(None, "Already running!", "Error", wx.OK).ShowModal()
            return
        actions = self.handler.ParseScript(self.control.GetValue())
        print(actions)
        self.handler.running = True
        self.handler.pause = False
        thread = threading.Thread(target=self.handler.RunScript, daemon=True, args=(actions,))
        thread.start()
        #self.handler.RunScript(actions)

    def OnStopScript(self, e):
        if not self.handler.running:
            wx.MessageDialog(None, "No script running!", "Error", wx.OK).ShowModal()
            return
        self.handler.StopScript()

    def OnPauseScript(self, e):
        if not self.handler.running:
            wx.MessageDialog(None, "No script running!", "Error", wx.OK).ShowModal()
            return
        self.handler.PauseScript()

    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, self.config["description"], "About " + self.config["name"], wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)

    def SetTopBar(self):
        openKeyName = self.keys["open"]["key"]
        saveKeyName = self.keys["save"]["key"]
        runKeyName = self.keys["run"]["key"]
        pauseKeyName = self.keys["pause"]["key"]
        stopKeyName = self.keys["stop"]["key"]
        if self.keys["open"]["ctrl"]:
            openKeyName = "CTRL+" + self.keys["open"]["key"]
        if self.keys["save"]["ctrl"]:
            saveKeyName = "CTRL+" + self.keys["save"]["key"]
        if self.keys["run"]["ctrl"]:
            runKeyName = "CTRL+" + self.keys["run"]["key"]
        if self.keys["pause"]["ctrl"]:
            pauseKeyName = "CTRL+" + self.keys["pause"]["key"]
        if self.keys["stop"]["ctrl"]:
            stopKeyName = "CTRL+" + self.keys["stop"]["key"]

        file_menu = wx.Menu()
        menu_openfile = file_menu.Append(wx.ID_OPEN, 'Open', " Open a file ("+ openKeyName +")")
        menu_savefile = file_menu.Append(wx.ID_SAVE, 'Save', " Save a file (" + saveKeyName + ")")
        menu_savefileas = file_menu.Append(wx.ID_SAVEAS, 'Save as', " Save as")
        menu_exit = file_menu.Append(wx.ID_EXIT, "Exit", " Exit the app (ALT+F4)")

        help_menu = wx.Menu()
        menu_about = help_menu.Append(wx.ID_ABOUT, "About", " About this app")

        script_menu = wx.Menu()
        menu_run = script_menu.Append(wx.ID_ANY, "Run", " Run the script (" + runKeyName + ")")
        menu_pause = script_menu.Append(wx.ID_ANY, "Pause", " Pause the script (" + pauseKeyName + ")")
        menu_stop = script_menu.Append(wx.ID_ANY, "Stop", " Stop the script (" + stopKeyName + ")")

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "File")
        menu_bar.Append(script_menu, "Script")
        menu_bar.Append(help_menu, "Help")
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.OnOpen, menu_openfile)
        self.Bind(wx.EVT_MENU, self.OnSave, menu_savefile)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menu_savefileas)
        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menu_about)
        self.Bind(wx.EVT_MENU, self.OnRun, menu_run)
        self.Bind(wx.EVT_MENU, self.OnPauseScript, menu_pause)
        self.Bind(wx.EVT_MENU, self.OnStopScript, menu_stop)
