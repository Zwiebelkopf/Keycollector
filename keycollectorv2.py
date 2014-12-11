#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 21.11.2014

@author: DBernhardt
@version: 2.0
'''
import wx, sys
from Crypto.Cipher import AES
import hashlib, binascii, string, random

try:
    from agw import genericmessagedialog as GMD
except ImportError:
    import wx.lib.agw.genericmessagedialog as GMD

class Frame(wx.Frame):
    def __init__(self, title, filename=""):
        wx.Frame.__init__(self,None,-1,title=title,pos=(175,175), size=(600,300))
        self.Centre()
        self.filename = filename        # Dateiname
        self.awesome = ""               # Passwort
        self.contentNotSaved = True     # Änderungen an Datei vorgenommen
        self.liste = {}
        
        self.CreateMenu()
        self.CreateInterface()
        if self.filename != "":
            self.OnOpen(None)
    
    def CreateMenu(self):
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        d_neu = menu.Append(wx.ID_ANY, "Neuer Eintrag/Bearbeiten\tCtrl+F","Neuen oder vorhanden Eintrag bearbeiten")
        self.Bind(wx.EVT_MENU, self.OnNeu, d_neu)
        d_open = menu.Append(wx.ID_ANY, "Öffnen\tCtrl+T", "Öffne Passwortdatei")
        self.Bind(wx.EVT_MENU, self.OnOpen, d_open)
        d_save = menu.Append(wx.ID_ANY, "Speichern\tCtrl+S", "Anlegen neuer Schulden oder Auslagen.")
        self.Bind(wx.EVT_MENU, self.OnSave, d_save)
        d_saveas = menu.Append(wx.ID_ANY, "Speichern unter...\tCtrl+Shift+S", "neue Passwortdatei auswählen")
        self.Bind(wx.EVT_MENU, self.OnSaveAs, d_saveas)
        d_exit = menu.Append(wx.ID_EXIT, "Beenden\tCtrl+Q", "Beendet das Programm.")
        self.Bind(wx.EVT_MENU, self.OnClose, d_exit)
        menuBar.Append(menu, "Datei")
        self.SetMenuBar(menuBar)
    
    def CreateInterface(self):
        self.font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.panel = wx.Panel(self,-1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)   # gesamtes Bild
        vbox = wx.BoxSizer(wx.VERTICAL)     # rechte Seite
        vbox2 = wx.BoxSizer(wx.VERTICAL)    # Filter + Serverliste
        
        self.filter = wx.TextCtrl(self.panel)
        self.serverListBox = wx.ListBox(self.panel, choices=[])
        self.userliste = wx.ComboBox(self.panel, size=(200,-1), choices=[])
        self.passwort = wx.TextCtrl(self.panel,size=(400,30),style=0)
        
        self.serverListBox.SetFont(self.font1)
        self.filter.SetFont(self.font1)
        self.userliste.SetFont(self.font1)
        self.passwort.SetFont(self.font1)
        
        vbox.Add(self.userliste, 1, wx.CENTER|wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(self.passwort, 1, wx.CENTER|wx.ALIGN_CENTER_VERTICAL)
        
        vbox2.Add(self.filter,1,wx.TOP|wx.EXPAND)
        vbox2.Add(self.serverListBox,10,wx.EXPAND)
        
        hbox.Add(vbox2,1,wx.EXPAND)
        hbox.Add(vbox,3,wx.EXPAND)
        self.panel.SetSizer(hbox)
        
        self.Bind(wx.EVT_TEXT, self.OnFilter, self.filter)
        self.Bind(wx.EVT_LISTBOX, self.OnChangeServer, self.serverListBox)
        self.Bind(wx.EVT_COMBOBOX, self.OnChangeUser, self.userliste)
    
    def OnFilter(self,event):
        self.serverListBox.Clear()
        
        pos = 0
        for item in self.liste:
            if string.find(item.lower(),self.filter.GetValue()) > -1:
                self.serverListBox.Insert(item,pos)
                pos += 1
    
    def OnChangeServer(self,event):
        self.userliste.Clear()
        self.passwort.SetValue("")
        pos = 0
        for item in self.liste[self.serverListBox.GetString(self.serverListBox.GetSelection())]:
            self.userliste.Insert(item,pos)
            pos += 1
    
    def OnChangeUser(self,event):
        self.passwort.SetValue("")
        aktserv = self.serverListBox.GetString(self.serverListBox.GetSelection())
        user = self.userliste.GetString(self.userliste.GetSelection())
        pw = self.liste[aktserv][user]
        self.passwort.SetValue(pw)
    
    def OnNeu(self,event):
        dlg = NewFrame(self.liste,self.font1)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            try:
                self.liste[str(dlg.server.GetValue())].update({str(dlg.user.GetValue()):str(dlg.pw.GetValue())})
            except:
                self.liste[str(dlg.server.GetValue())] = {str(dlg.user.GetValue()):str(dlg.pw.GetValue())}
            self.RefreshServerListe()
        dlg.Destroy()
    
    def OnSave(self,event):
        if self.filename == "":
            self.OnSaveAs(event)
        else:
            txt = "key.txt\n"
            for obj in self.liste:
                txt = txt + obj+"\n"
                zw = ""
                for var in self.liste[obj]:
                    zw = zw + var+"="+self.liste[obj][var]+";"
                txt = txt + zw[0:-1] + "\n"
            if len(txt)% 16 != 0:
                fehlt = 16-(len(txt) % 16)
                for i in range(0,fehlt-len(str(fehlt))):
                    txt = '#' + txt
                txt = str(fehlt) + txt
            encobj = AES.new(self.awesome, AES.MODE_ECB)
            ciphertext = encobj.encrypt(txt)
            try:
                datei = open(self.filename,"w")
                datei.write(ciphertext.encode('hex'))
                datei.close()
                dlg = GMD.GenericMessageDialog(self, "erfolgreich gespeichert.","INFO",wx.OK | wx.ICON_INFORMATION)
            except:
                dlg = GMD.GenericMessageDialog(self, "Speichern fehlgeschlagen","ERROR",wx.OK | wx.ICON_ERROR)
                pass
            res = dlg.ShowModal()
    
    def OnSaveAs(self,event):
        if self.awesome == "":
            self.onDialog(event)
        dlg = wx.FileDialog(self, "Speichern unter ...","","","",wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            dlg.Destroy()
        self.OnSave(event)
    
    def OnOpen(self,event):
        if self.filename == "":
            if self.contentNotSaved:
                dlg = wx.FileDialog(self, "Open XYZ file", "", "", "", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
                if dlg.ShowModal() == wx.ID_OK:
                    self.filename = dlg.GetPath()
                    dlg.Destroy()
                else: # Auswahl wurde abgebrochen
                    return -1
        self.onDialog(None)
        
        i = 0
        aktserv = ""
        datei = open(self.filename,"r")
        crypted = datei.read()
        datei.close()
        ciphertext = binascii.unhexlify(crypted)
        decobj = AES.new(self.awesome, AES.MODE_ECB)
        datei = decobj.decrypt(ciphertext)
        test = string.find(datei,'#')
        if test == -1:
            datei = datei
        elif test == 1:
            var = int(datei[0])
            datei = datei[var:]
        elif test == 2:
            var = int(datei[0]+''+datei[1])
            datei = datei[var:]
        line = ""
        for zeichen in datei:
            if zeichen == "\n":
                i+=1
                if i%2==0:
                    self.liste[line] = {}
                    aktserv = line
                elif i > 1:
                    self.liste[aktserv] = dict(item.split("=") for item in line.split(";"))
                line = ""
            else:
                line = line + zeichen
        self.RefreshServerListe()
    
    def OnClose(self,event):
        self.Destroy()
    
    def onDialog(self, event):
        dlg = PWFrame()
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            self.CheckPW(dlg.password.GetValue())
        dlg.Destroy()
    
    def CheckPW(self, value):
        m = hashlib.md5()
        m.update(value)
        self.awesome = m.hexdigest()
    
    def RefreshServerListe(self):
        self.serverListBox.Clear()
        self.userliste.Clear()
        self.passwort.SetValue("")
        pos = 0
        for key in sorted(self.liste.keys(),key=str.lower):
            self.serverListBox.Insert(key,pos)
            pos += 1

class PWFrame(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="Dialog")
        self.Centre()
        self.SetSize((200, 100))
        
        self.password = wx.TextCtrl(self,size=(150,-1),style=wx.TE_PASSWORD)
        okBtn = wx.Button(self, wx.ID_OK)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.password, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(okBtn, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(sizer)

class NewFrame(wx.Dialog):
    def __init__(self, liste,font):
        wx.Dialog.__init__(self,None,title="Neuer Eintrag")
        self.Centre()
        self.font1 = font
        self.liste = liste
        self.SetSize((300,175))
        vbox = wx.BoxSizer(wx.VERTICAL)
        hboxSer = wx.BoxSizer(wx.HORIZONTAL)
        hboxUse = wx.BoxSizer(wx.HORIZONTAL)
        hboxPas = wx.BoxSizer(wx.HORIZONTAL)
        hboxBut = wx.BoxSizer(wx.HORIZONTAL)
        self.server = wx.ComboBox(self,size=(180,25))
        self.user = wx.ComboBox(self,size=(180,25))
        self.pw = wx.TextCtrl(self)
        okBtn = wx.Button(self, wx.ID_OK)
        caBtn = wx.Button(self, wx.ID_CANCEL)
        genBtn = wx.Button(self,wx.ID_NEW)
        self.Bind(wx.EVT_BUTTON, self.GeneratePw, genBtn)
        self.Bind(wx.EVT_COMBOBOX, self.OnChangeServer, self.server)
        
        self.server.SetFont(self.font1)
        self.user.SetFont(self.font1)
        self.pw.SetFont(self.font1)
        
        hboxSer.Add(wx.StaticText(self,-1,"Server"),1,wx.EXPAND)
        hboxSer.Add(self.server,2,wx.EXPAND)
        
        hboxUse.Add(wx.StaticText(self,-1,"User"),1,wx.EXPAND)
        hboxUse.Add(self.user,2,wx.EXPAND)
        
        hboxPas.Add(wx.StaticText(self,-1,"Passwort"),1,wx.EXPAND)
        hboxPas.Add(self.pw,1,wx.EXPAND)
        hboxPas.Add(genBtn,1,wx.EXPAND)
        
        hboxBut.Add(okBtn,1,wx.EXPAND)
        hboxBut.Add(caBtn,1,wx.EXPAND)
        
        vbox.Add(hboxSer,1,wx.EXPAND)
        vbox.Add(hboxUse,1,wx.EXPAND)
        vbox.Add(hboxPas,1,wx.EXPAND)
        vbox.Add(hboxBut,1,wx.EXPAND)
        
        self.SetSizer(vbox)
        self.FillValues()
    
    def FillValues(self):
        pos = 0
        for key in sorted(self.liste.keys(),key=str.lower):
            self.server.Insert(key,pos)
            pos += 1
    
    def GeneratePw(self,event):
        option1 = {} # Buchstaben (groß)
        option2 = {} # Zahlen
        option3 = {} # Buchstaben (klein)

        for i in range(0,26):
            option1[i] = chr(65+i)
        for i in range(0,10):
            option2[i] = i
        for i in range(0,26):    
            option3[i] = chr(97+i)
        
        locals()['option1'] = option1
        locals()['option2'] = option2
        locals()['option3'] = option3
        
        erg = ""
        i=1
        while len(erg) < 8:
            wert = random.randint(0,2)
            try:
                zufall = random.randint(0,len(locals()["option"+str(wert+1)])-1)
                erg = erg + str(locals()["option"+str(wert+1)][zufall])
                i += 1
            except:
                pass
    
        self.pw.SetValue("")
        self.pw.SetValue(erg)
    
    def OnChangeServer(self,event):
        self.user.Clear()
        self.pw.SetValue("")
        pos = 0
        for item in self.liste[self.server.GetString(self.server.GetSelection())]:
            self.user.Insert(item,pos)
            pos += 1

if __name__ == '__main__':
    app = wx.App(0)
    if len(sys.argv) > 1:
        top = Frame("Hallo",sys.argv[1])
    else:
        top = Frame("Hallo")
    top.Show()
    app.MainLoop()
