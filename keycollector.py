#!/path/to/python

from Tkinter import *
from Crypto.Cipher import AES
import binascii,string,hashlib,tkFileDialog

## Menüleisten optionen
## open = Datei->Öffnen
## new = Datei->Neu
## save = Datei->Speichern
def callback(test="huhu"):
  if test == "open":
		Servers.delete(0,END)
		Users.delete(0,END)
		PWfeld.delete(1.0,END)
		datei = tkFileDialog.askopenfile(parent=root,mode='r',title="Choose a crypted file")
		i = 0
		aktserv = ""
		nliste = {}
		crypted = datei.read()
		datei.close()
		ciphertext = binascii.unhexlify(crypted) 
		decobj = AES.new(awesome, AES.MODE_ECB)
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
					liste[line] = {}
					aktserv = line
				elif i > 1:
					liste[aktserv] = dict(item.split("=") for item in line.split(";"))
				line = ""
			else:
				line = line + zeichen
		for key in sorted(liste.keys(),key=str.lower):
			Servers.insert(END,key)
	elif test == "new":
		if e2.get() != "" and e3.get() != "" and e4.get != "":
			try:
				var = str(liste[e2.get()])
			except:
				var = {}
			if len(var) > 2:
				var = var[0:-1] + "," + "'" + e3.get() + "':'"+e4.get()+"'}"
			else:
				var = "{'"+ e3.get() +"':'"+ e4.get() +"'}"
			liste[e2.get()] = eval(var)
			Servers.delete(0,END)
			Users.delete(0,END)
			PWfeld.delete(1.0,END)
			for key in sorted(liste.keys(),key=str.lower):
				Servers.insert(END,key)
			if choosenSRV != "":
				for key in liste[choosenSRV]:
					Users.insert(END,key)
			
	elif test == "save":
		txt = "key.txt\n"
		print liste
		for obj in liste:
			txt = txt + obj+"\n"
			zw = ""
			for var in liste[obj]:
				zw = zw + var+"="+liste[obj][var]+";"
			txt = txt + zw[0:-1] + "\n"
		if len(txt)% 16 != 0:
			fehlt = 16-(len(txt) % 16)
			for i in range(0,fehlt-len(str(fehlt))):
				txt = '#' + txt
			txt = str(fehlt) + txt
		encobj = AES.new(awesome, AES.MODE_ECB)
		ciphertext = encobj.encrypt(txt)
		datei = tkFileDialog.asksaveasfile(parent=root,mode='w',title="Choose a file to save")
		datei.write(ciphertext.encode('hex'))
		datei.close()

## Bei einem Linksklick wird der ausgewählte Server ausgelesen und alle Benutzer werden im
## mittleren (Users) Fenster angezeigt. Alte Werte werden vorher gelöscht.
def read_server(event):
	global choosenSRV
	try:
		index = Servers.curselection()[0]
		seltext = Servers.get(index)
		choosenSRV = seltext
		Users.delete(0,END)
		PWfeld.delete(1.0,END)
		e2.delete(0,END)
		e3.delete(0,END)
		e4.delete(0,END)
		e2.insert(0,seltext)
		for key in liste[seltext]:
			Users.insert(END,key)
	except:
		a = True

## Bei einem Linksklick wird das entsprechende Passwort zum ausgewählten User im rechten
## Fenster angezeigt
def read_pw(event):
	global choosenSRV
	try:
		index = Users.curselection()[0]
		seltext = Users.get(index)
		e3.delete(0,END)
		e4.delete(0,END)
		e3.insert(0,seltext)
		PWfeld.delete(1.0,END)
		PWfeld.insert(INSERT,liste[choosenSRV][seltext])
	except:
		a = True

def exit():
	sys.exit()
	
## Eigentliches Passwortfenster wird hier aufgebaut und das vorher eingegebene Passwort
## wird für alle folgenden Dateien genutzt.
def check_PW(event=False):
	global awesome
	m = hashlib.md5()
	m.update(e1.get())
	awesome = m.hexdigest()
	e1.pack_forget()
	e1.delete(0,END)
	b1.pack_forget()
	menu.add_cascade(label="Datei",menu=filemenu)
	filemenu.add_command(label="Neu",command=lambda:callback("new"))
	filemenu.add_command(label="Öffnen",command=lambda:callback("open"))
	filemenu.add_command(label="Speichern",command=lambda:callback("save"))
	filemenu.add_command(label="Beenden",command=exit)
	Servers.grid(row=1,column=1)
	Users.grid(row=1,column=2)
	PWfeld.grid(row=1,column=3)
	e2.grid(row=2,column=1)
	e3.grid(row=2,column=2)
	e4.grid(row=2,column=3)
	#scrollbar.pack(side=RIGHT, fill=Y)
	#Servers.config(yscrollcommand=scrollbar.set)
	#scrollbar.config(command=Servers.yview)


def return_new(event):
	callback('new')
	
def remove_server(event):
	if event.keysym == "Delete":
		index = Servers.curselection()[0]
		seltext = Servers.get(index)
		del liste[seltext]
		Servers.delete(0,END)
		Users.delete(0,END)
		PWfeld.delete(1.0,END)
		for key in liste:
			Servers.insert(END,key)

def remove_user(event):
	global choosenSRV
	if event.keysym == "Delete":
		index = Users.curselection()[0]
		seltext = Users.get(index)
		del liste[choosenSRV][seltext]
		Servers.delete(0,END)
		Users.delete(0,END)
		PWfeld.delete(1.0,END)
		for key in liste:
			Servers.insert(END,key)
		for key in liste[choosenSRV]:
			Users.insert(END,key)

#################################
root = Tk()
root.title("Passwortsammler")
awesome = ""

e1 = Entry(root,show="*")
e1.pack()
e1.focus_set()
e1.bind('<Return>',check_PW)
b1 = Button(root,text="prüfen",command=check_PW)
b1.pack()
	
liste = {}

menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
scrollbar = Scrollbar(root)
Servers = Listbox(root,selectmode=BROWSE)
Servers.bind('<ButtonRelease-1>', read_server)
Servers.bind('<Key>',remove_server)
Users = Listbox(root)
Users.bind('<ButtonRelease-1>',read_pw)
Users.bind('<Key>',remove_user)
PWfeld = Text(root)
PWfeld.config(width=20, height=9)
choosenSRV = ""
e2 = Entry(root)
e3 = Entry(root)
e4 = Entry(root)
e4.bind('<Return>',return_new)
		
root.mainloop()
