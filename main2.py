if __name__ == '__main__':
	import sys, os
	from scripts.outgame import frame, master
	if getattr(sys, 'frozen', False):
		os.chdir(sys._MEIPASS)
	master_ = master.Master()
	sign_in = frame.Sign_In(master_)
	master_.mainloop()
