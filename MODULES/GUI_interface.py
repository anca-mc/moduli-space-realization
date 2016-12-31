from MODULES.proj_points import *
import sys
from Tkinter import *
import tkMessageBox

class TextRedirector(object):
	def __init__(self, widget, tag="stdout"):
		self.widget = widget
		self.tag = tag

	def write(self, str):
		self.widget.configure(state=NORMAL)
		self.widget.insert(END, str, (self.tag))
		self.widget.configure(state=DISABLED)

class GUIwindow(object):
	def __init__(self):
		self.top = Tk()
		self.frame = Frame(self.top)
		self.frame.grid(row = 0, column = 0, sticky = "nsew")
		self.L1 = Label(self.top, text = "Input multiple points")
		self.L1.grid(row = 0, column = 0, sticky = "nsew")
		self.e1 = Entry(self.top)
		self.e1.grid(row = 0, column = 1, sticky = "nsew")
		self.b1 = Button(self.top, text = "Clear", command = lambda: self.clearCallback(self.e1))
		self.b1.grid(row = 0, column = 2, columnspan = 2, sticky = "nsew")
		self.L2 = Label(self.top, text = "Input arrangement cardinal")
		self.L2.grid(row = 1, column = 0, sticky = "nsew")
		self.e2 = Entry(self.top)
		self.e2.grid(row = 1, column = 1, sticky = "nsew")
		self.b2 = Button(self.top, text = "Clear", command = lambda: self.clearCallback(self.e2))
		self.b2.grid(row = 1, column = 2,  columnspan = 2, sticky = "nsew")
		self.b5 = Button(self.top, text = 'Compute', command = self.compute_config_space)
		self.b5.grid(row = 3, column = 0, sticky = "nsew")
		self.scrollbar = Scrollbar(self.top)
		self.scrollbar.grid(row=2, column=5, sticky = 'nsew')
		self.text = Text(self.top, wrap = "word", yscrollcommand = self.scrollbar.set, pady = 10, padx = 10)
		self.text.config(state="disabled")
		self.text.grid(row = 2, column = 0, columnspan = 4)
		self.text.tag_configure("stderr", foreground="#b22222")
		self.scrollbar.config(command=self.text.yview)
		self.b6 = Button(self.top, text = 'Save to file', command = lambda: self.saveOutput(self.text))
		self.b6 .grid(row = 3, column = 1, sticky = "nsew")
		sys.stdout = TextRedirector(self.text, "stdout")
		sys.stderr = TextRedirector(self.text, "stderr")
		self.b3 = Button(self.top, text = "Clear Output", command = lambda: self.clearText(self.text))
		self.b3.grid(row = 3, column = 2, sticky = "nsew")
		Button(self.top, text = 'Quit', command=self.top.quit).grid(row = 3, column = 3, sticky = "nsew")

	def clearCallback(self, e):
		e.delete(0, END)

	def writeOutput(self, str):
		self.text.config(state=NORMAL)
		self.text.insert(END, str)
		self.text.config(state=DISABLED)

	def clearText(self, text):
		text.config(state=NORMAL)
		text.delete(1.0,END)
		text.configure(state=DISABLED)

	def saveOutput(self, text):
		with open("IO.txt", 'a') as outfile:
			outfile.write(text.get(1.0, END))

	def input_error(self):
		tkMessageBox.showerror("Error", "incorrect input!")

	def compute_config_space(self):
		try:
			points = input_points(self.e1.get())
			arr_cardinal = int(self.e2.get())
			self.writeOutput(' multiple points = {} \n arrangement cardinal = {} \n \n'.format(self.e1.get(), self.e2.get()))
			config = Combinatorial_Configuration(points, arr_cardinal)
			if config.validate_input_points() and config.validate_arrangement_cardinal():
				if not config.test_pencil_like(arr_cardinal):
					if not config.test_almost_pencil_like(arr_cardinal):
						config.describe_realization_space(arr_cardinal)
		except:
			self.input_error()

	def run(self):
		self.top.mainloop()