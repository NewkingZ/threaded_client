#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this module contains The main client code

import sys
import threading
import queue
import time
from tkinter import *
from time import sleep

CLOSING_THREAD = "Closing"
INPUT_THREAD = "Input"


def do_nothing():
	print("Nyanpasu")


class ThreadedClient:
	"""
	App running two threads simultaneously (GUI + serial). Initialization starts the gui, then periodically checks
	incoming data as well as its shutdown condition
	"""
	def __init__(self, window, title, version):
		self.window = window

		# Setup gui
		self.gui = AppGUI(self.window, title, self.kermit, version)
		# Setup threads (Start with 1 for now)
		self.running = 1

		# Start the periodic call that checks GUI queue
		self.periodic_call()

	def periodic_call(self):
		"""
		Function called every 100ms and check to see if its time to shut down
		"""
		self.gui.process_incoming()
		if not self.running:
			# Exit condition
			# Insert Cleanup here
			sys.exit(1)
		self.window.after(100, self.periodic_call)

	def kermit(self):
		"""
		Shutdown function for the window
		"""
		self.running = 0


class AppGUI:
	"""
	GUI app with functions tied to handlers
	"""
	def __init__(self, window: Tk, title, shutdown, version):
		self.threads = []
		self.window = window
		self.version = version
		self.shutdown = shutdown

		# System variables
		self.collect_data = False				# Input collection flag
		self.content_queue = queue.Queue()		# Input collection queue

		def close():
			"""Starts the closing thread"""
			if "closing" not in self.threads:
				# Destroy top level windows
				self.threads.append(CLOSING_THREAD)

				self.collect_data = False
				self.shutdown()

		self.close = close  # Shutdown function for the app
		self.window.protocol("WM_DELETE_WINDOW", close)

		self.window.title(title)
		self.window.geometry("1200x800")
		self.window.minsize(800, 600)
		self.window.grid_propagate(False)
		self.window.columnconfigure(10, weight=1)
		self.window.columnconfigure(20, weight=2)
		self.window.rowconfigure([10, 20], weight=1)

		self.collection_state_label_var = StringVar()
		self.collection_state_label = Label(self.window, textvariable=self.collection_state_label_var,
											font=("calibri, 20"))
		self.start_button = Button(self.window, text="Start", font=("calibri, 20"), command=self.collection_start)
		self.stop_button = Button(self.window, text="Stop", font=("calibri, 20"), command=self.collection_stop)
		self.status_text = Text(self.window, width=20)

		self.start_button.grid(row=10, column=10, padx=80, pady=80, sticky="news")
		self.stop_button.grid(row=20, column=10, padx=80, pady=80, sticky="news")
		self.status_text.grid(row=10, rowspan=21, column=20, padx=80, pady=80, sticky="news")
		self.collection_state_label.grid(row=25, column=10, padx=20, pady=50, sticky="news")

		self.collection_state_label_var.set("Current State: Off")

	def collection_start(self):
		if not self.collect_data:
			self.collection_state_label_var.set("Current State: On")
			input_thread = threading.Thread(target=self.open_input_socket_or_whatever_data_source_you_want_to_use)
			input_thread.start()

	def collection_stop(self):
		if self.collect_data:
			self.collection_state_label_var.set("Current State: Off")
			self.collect_data = False

	def process_incoming(self):
		while self.content_queue.qsize() > 0:
			try:
				new_line = self.content_queue.get().decode().strip('\r\n').lower()
				self.status_text.insert(END, new_line + "\n")
			except UnicodeDecodeError as err:
				print("Error decoding line")
			except queue.Empty:
				pass

	def open_input_socket_or_whatever_data_source_you_want_to_use(self):
		while INPUT_THREAD in self.threads:
			self.collect_data = False

		self.threads.append(INPUT_THREAD)
		self.collect_data = True

		last_time = time.time()
		while self.collect_data:
			# Check for data and add it to queue
			if time.time() - last_time > 1:
				self.content_queue.put("new data received".encode())
				last_time = time.time()
			sleep(.02)

		self.threads.remove(INPUT_THREAD)
