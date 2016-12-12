import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from copy import deepcopy
from misc import ScrolledText
from network import Network

def center_frame(ws, hs, w, h):
	x = (ws / 2) - (w / 2)
	y = (hs / 2) - (h / 2)
	return '%dx%d+%d+%d' % (w, h, x, y)
def get_color(tup):
	return '#%02x%02x%02x' % tup
class Sign_In(tk.Frame):
	MAX_TEXT_LENGTH = 6
	WIDTH = 180
	HEIGHT = 160
	def __init__(self, master):
		super().__init__(master)
		master.title('Sign In')
		master.child = self
		ws = master.winfo_screenwidth()
		hs = master.winfo_screenheight()
		master.geometry(center_frame(ws, hs, Sign_In.WIDTH, Sign_In.HEIGHT))
		self.pack()
		self.create_widgets()
	def create_widgets(self):
		up_frame = tk.Frame(self)
		up_frame.pack(pady=5, padx=5)
		user_label = tk.Label(up_frame, text='Your username:')
		user_label.pack(side='left')
		sv = tk.StringVar()
		sv.trace('w', lambda name, index, mode, sv=sv: self.callback(sv))
		self.user_entry = tk.Entry(up_frame, textvariable=sv)
		self.user_entry.pack(side='right')

		ip_frame = tk.Frame(self)
		ip_frame.pack(pady=5, padx=5)
		ip_label = tk.Label(ip_frame, text='Your IPv4:')
		ip_label.pack(side='left')
		self.ip_entry = tk.Entry(ip_frame)
		self.ip_entry.pack(side='right')
		ipv4 = Network.get_ip()
		if ipv4 != None:
			self.ip_entry.insert('end', ipv4)
			self.ip_entry.configure(state='readonly')

		self.host = tk.Button(self, text='Host', command=lambda : self.host_action())
		self.host.pack(pady=2, padx=5)

		mid_frame = tk.Frame(self)
		mid_frame.pack(pady=5, padx=5)
		host_label = tk.Label(mid_frame, text='Host:')
		host_label.pack(side='left')
		self.host_entry = tk.Entry(mid_frame)
		self.host_entry.pack(side='right')
		
		self.join = tk.Button(self, text='Join', command=lambda : self.join_action())
		self.join.pack(pady=2, padx=5)
	def callback(self, sv):
		sv.set(sv.get()[:6])
	def host_action(self):
		if len(self.user_entry.get()) == 0:
			messagebox.showerror("Invalid username", "Username cannot be empty")
		elif len(self.ip_entry.get()) == 0:
			messagebox.showerror("Invalid IPv4", "IPv4 cannot be empty")
		else:
			result = self.master.host(self.user_entry.get(), self.ip_entry.get())
			if result:
				self.destroy()
			else:
				messagebox.showerror("Invalid IPv4", "Bad IPv4")
	def join_action(self):
		if len(self.user_entry.get()) == 0:
			messagebox.showerror("Invalid username", "Username cannot be empty")
		elif len(self.host_entry.get()) == 0:
			messagebox.showerror("Invalid host", "Host cannot be empty")
		else:
			self.master.join(self.user_entry.get(), self.host_entry.get())

class Team_Room(tk.Frame):
	WIDTH = 590
	HEIGHT = 400
	NOT_READY_COLOR = 'white'
	READY_COLOR = '#FCD878'
	HOST_COLOR = '#D70000'
	def __init__(self, master, team_config, server_ip, host_name):
		super().__init__(master)
		self.host_name = host_name
		self.master = master
		self.owner = master.owner
		self.server_ip = server_ip
		master.child = self
		master.title('Waiting room of ' + host_name + ' at ' + server_ip)
		ws = master.winfo_screenwidth()
		hs = master.winfo_screenheight()
		master.geometry(center_frame(ws, hs, Team_Room.WIDTH, Team_Room.HEIGHT))
		self.team_config = team_config
		self.pack()
		self.create_widgets()
	def update(self, team_config, msg_li):
		n_player = self.team_config.MAX_PLAYER_PER_TEAM
		change_dic = {}
		for r, row in enumerate(self.frames):
			for c, frame in enumerate(row):
				index = r + c * n_player
				if frame.name != None:
					if frame.name not in team_config.players and (r, c) not in change_dic:
						change_dic[(r, c)] = None
					elif self.team_config.players[frame.name] != team_config.players[frame.name]:
						new_player = team_config.players[frame.name]
						ro = new_player['index'] % n_player
						co = new_player['index'] // n_player
						new_frame = self.frames[ro][co]
						if frame not in change_dic:
							change_dic[(r, c)] = None
						change_dic[(ro, co)] = team_config.players[frame.name]
				else:
					for player in team_config.players.values():
						if player['index'] == index:
							change_dic[(r, c)] = player
							break
		for r, c in change_dic:
			self.frames[r][c].pack_forget()
			self.frames[r][c] = self.render_player(self.team_frame, change_dic[(r, c)])
			dic = {'row' : r + 1, 'column' : c, 'pady' : 2, 'padx' : 5}
			self.frames[r][c].grid(**dic)
		self.team_config = team_config
		if self.host_name == self.owner and (not self.team_config.is_start_possible() or not self.map_entry.get()):
			self.ready.configure(state='disabled')
		else:
			self.ready.configure(state='normal')
		self.area_text.configure(state='normal')
		for msg in msg_li:
			self.area_text.insert('end', msg + '\n')
			st = msg.index('[') + 1
			end = msg.index(']')
			name = msg[st:end]
			line = int(self.area_text.index('end').split('.')[0]) - 2
			st = str(line) + '.' + str(st)
			end = str(line) + '.' + str(end)
			if name == self.host_name:
				self.area_text.tag_add("host", st, end)
			elif name == self.owner:
				self.area_text.tag_add("owner", st, end)
		self.area_text.configure(state='disabled')
		self.area_text.see('end')
	def create_widgets(self):
		self.team_frame = tk.Frame(self)
		self.team_frame.pack()
		style = ttk.Style()
		for key in self.team_config.COLOR_LIST:
			color = get_color(self.team_config.COLOR_LIST[key])
			style_name = key + '.TCombobox'
			style.map(style_name, selectbackground=[('readonly', color), ('disabled', color)])
			style.map(style_name, fieldbackground=[('readonly', color), ('disabled', color)])
			style.map(style_name, foreground=[('readonly', 'black'), ('disabled', 'black')])
			style.map(style_name, selectforeground=[('readonly', 'black'), ('disabled', 'black')])
		tk.Button(self.team_frame, text='Team 1', bg='blue', command=lambda:self.signal_team_change(self.team_config.TEAM1)).grid(row=0, column=0, pady=2, padx=5)
		tk.Button(self.team_frame, text='Team 2', bg='red', command=lambda:self.signal_team_change(self.team_config.TEAM2)).grid(row=0, column=1, pady=2, padx=5)
		n_player = self.team_config.MAX_PLAYER_PER_TEAM
		indexs = [x for x in range(n_player * 2)]
		for player in self.team_config.players.values():
			indexs[player['index']] = player['name']
		self.frames = [[None, None] for x in range(n_player)]
		for i, name in enumerate(indexs):
			c = i // n_player
			r = i % n_player
			dic = {'row' : r + 1, 'column' : c, 'pady' : 2, 'padx' : 5}
			if type(name) == str:
				frame = self.render_player(self.team_frame, self.team_config.players[name])
				frame.grid(**dic)
			else:
				frame = self.render_player(self.team_frame)
				frame.grid(**dic)
			self.frames[r][c] = frame
		owner = self.team_config.players[self.owner]
		mid_frame = tk.Frame(self, pady=10)
		mid_frame.pack()
		self.area_text = ScrolledText(mid_frame, height=10)
		self.area_text.edit_modified(False)
		self.area_text.insert('end', "Welcome to {host}'s waiting room. Type something to chat\n".format(host=self.host_name))
		self.area_text.pack(fill='x')
		self.area_text.tag_config('host', foreground='red')
		self.area_text.tag_config('owner', foreground='blue')
		trans_frame = tk.Frame(mid_frame, pady=5)
		trans_frame.pack(fill='x')
		tk.Label(trans_frame, text=self.owner+':').pack(side='left')
		self.text = tk.Entry(trans_frame, width=65)
		self.text.bind('<Return>', self.signal_text)
		self.text.pack(side='left', fill='x')
		bot_frame = tk.Frame(self)
		bot_frame.pack()
		if owner['status'] == self.team_config.HOST:
			text = 'Start'
		else:
			text = 'Ready'
		self.ready = tk.Button(bot_frame, text=text, command=self.signal_ready)
		quit = tk.Button(bot_frame, text='Quit', command=self.master.handle_quit)
		if self.host_name == self.owner:
			tk.Label(bot_frame, text='Map file:').pack(side='left')
			self.map_entry = tk.Entry(bot_frame, width=30, state='readonly')
			self.map_entry.pack(side='left')
			choose = tk.Button(bot_frame, text='Choose map', command=self.choose_map)
			choose.pack(side='left')
			self.ready.configure(state='disabled')
			quit.pack(side='right', padx=5)
			self.ready.pack(side='right', padx=30)
		else:
			quit.grid(row=n_player + 1, column=1, padx=20)
			self.ready.grid(row=n_player + 1, column=0, padx=20)
	def choose_map(self):
		file_name = filedialog.askopenfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')], title='Choose map file', parent=self.master)
		if len(file_name) == 0:
			return
		if self.team_config.is_start_possible():
			self.ready.configure(state='normal')
		self.master.handle_map(file_name)
		self.map_entry.configure(state='normal')
		self.map_entry.delete(0, 'end')
		self.map_entry.insert('end', file_name)
		self.map_entry.configure(state='readonly')
	def signal_text(self, event=None):
		text = self.text.get()
		if len(text) == 0:
			return
		else:
			self.text.delete(0, 'end')
			self.master.handle_chat(text)
	def signal_ready(self):
		if self.host_name == self.owner:
			self.master.start_game()
		else:
			player = deepcopy(self.team_config.players[self.owner])
			if player['status'] == self.team_config.NOT_READY:
				player['status'] = self.team_config.READY
				self.ready.configure(text='Not ready')
			else:
				player['status'] = self.team_config.NOT_READY
				self.ready.configure(text='Ready')
			self.master.handle_player_change(player)
	def signal_team_change(self, team):
		player = deepcopy(self.team_config.players[self.owner])
		if player['team'] != team:
			player['team'] = team
			self.master.handle_player_change(player)
	def signal_change(self, cbb):
		player = deepcopy(self.team_config.players[self.owner])
		player[cbb.key] = cbb.get()
		cbb.set(cbb.previous)
		self.master.handle_player_change(player)
	def render_player(self, master, player=None):
		if player == None:
			frame = tk.Frame(master, bg=Team_Room.NOT_READY_COLOR, bd=2)
			frame.name = None
			entry = tk.Entry(frame, state='disabled', width=33).pack()
		else:
			if player['status'] == self.team_config.NOT_READY:
				bg = Team_Room.NOT_READY_COLOR
			elif player['status'] == self.team_config.READY:
				bg = Team_Room.READY_COLOR
			else:
				bg = Team_Room.HOST_COLOR
			frame = tk.Frame(master, bg=bg, bd=2)
			frame.name = player['name']
			name = tk.Label(frame, text=player['name'])
			name.pack(side='left')
			state = 'disabled'
			if self.owner == player['name']:
				name.configure(fg='blue', font='arial 10 bold')
				state = 'readonly'
			tanks = ttk.Combobox(frame, width=14, state=state, justify='center', values=self.team_config.TANK_OPTION)
			tanks.set(player['tank'])
			tanks.previous = tanks.get()
			tanks.key = 'tank'
			tanks['style'] = player['color'] + '.TCombobox'
			tanks.bind('<<ComboboxSelected>>', lambda event: self.signal_change(tanks))
			tanks.pack(side='left')
			total = list(self.team_config.COLOR_LIST.keys())
			for plr in self.team_config.players.values():
				total.remove(plr['color'])
			colors = ttk.Combobox(frame, width=10, justify='center', state=state, values=total)
			colors.set(player['color'])
			colors.previous = colors.get()
			colors.key = 'color'
			colors['style'] = player['color'] + '.TCombobox' 
			colors.bind('<<ComboboxSelected>>', lambda event: self.signal_change(colors))
			colors.pack(side='left')
		return frame

