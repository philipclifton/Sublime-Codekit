import sublime_plugin
import subprocess
import sublime
import platform
import os
import sys
import os.path
from threading import Thread

# Fix windows imports
__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

if __path__ not in sys.path:
	sys.path.insert(0, __path__)

_pywinauto = os.path.join(__path__ + os.path.sep + 'win')
if _pywinauto not in sys.path:
	sys.path.insert(0, _pywinauto)

# Cache user operating system
_os = platform.system()


class SassListener(sublime_plugin.EventListener):
	def on_post_save_async(self, view):
		print('Sass Payload: Started!');

		if os.path.isfile(view.file_name()) and view.file_name().split('.')[-1] == 'scss':

			# Get file information from window
			fileName = view.file_name().split('/')[-1]
			destinFileName = fileName[:-4] + 'css' 
			projectPath = view.window().folders()[0];

			# Get the sass path from Project
			sassOrigin = projectPath + '/' + view.window().project_data()['folders'][0]['sass_origin']
			sassOutput = projectPath + '/' + view.window().project_data()['folders'][0]['sass_output']

			if os.path.isfile(sassOrigin + '/' + fileName) and os.path.isfile(sassOutput + '/' + destinFileName):

				# Command to run
				try:
					if view.window().project_data()['sass_debug'] is True:
						cmd = "sass --style compact --debug-info '{0}':'{1}' ".format(sassOrigin + '/' + fileName, sassOutput + '/' + destinFileName)
					else:
						cmd = "sass --style compact '{0}':'{1}' ".format(sassOrigin + '/' + fileName, sassOutput + '/' + destinFileName)
				except KeyError:
					cmd = "sass --style compact '{0}':'{1}' ".format(sassOrigin + '/' + fileName, sassOutput + '/' + destinFileName)


				# Run Command
				try:
					if view.window().project_data()['sass_compiler_active'] is False:
						x = None
					else:
						subprocess.Popen(cmd, shell=True);
						view.set_status('codekit', 'Sass compiled')	
				except KeyError:
				    subprocess.Popen(cmd, shell=True);
				    view.set_status('codekit', 'Sass compiled')	

			else:
				view.set_status('codekit', 'Sass project set incorrectly')

		else:
			view.set_status('codekit', 'File path incorrect')

		# Refresh Browser
		try:
		   	if view.window().project_data()['sass_browser_refresh'] is None:
		   		view.window().run_command('refresh_browsers');
		   	else:
		   		if view.window().project_data()['sass_browser_refresh'] is True:
		   			view.window().run_command('refresh_browsers');	
		except KeyError:
		    x = None


class set_sass_status(sublime_plugin.TextCommand):
	def run(self, edit):
		items = ['Compiler On', 'Compiler Off']
		self.view.window().show_quick_panel(items, self.on_done);

	def on_done(self, item):
		projectData = self.view.window().project_data()
		
		if item == 0:
			projectData['sass_compiler_active'] = True;
			self.view.set_status('codekit', 'Compiler On')
		else:
			projectData['sass_compiler_active'] = False;
			self.view.set_status('codekit', 'Compiler Off')

		self.view.window().set_project_data(projectData)


class set_browser_refresh(sublime_plugin.TextCommand):
	def run(self, edit):
		items = ['Browser Refresh On', 'Browser Refresh Off']
		self.view.window().show_quick_panel(items, self.on_done);

	def on_done(self, item):
		projectData = self.view.window().project_data()

		print(item)
		
		if item == 0:
			projectData['sass_browser_refresh'] = True;
			self.view.set_status('codekit', 'Browser Refresh On')
		else:
			projectData['sass_browser_refresh'] = False;
			self.view.set_status('codekit', 'Browser Refresh Off')

		self.view.window().set_project_data(projectData)


class set_debug_on(sublime_plugin.TextCommand):
		def run(self, edit):
			items = ['Debug On', 'Debug Off']
			self.view.window().show_quick_panel(items, self.on_done);

		def on_done(self, item):
			projectData = self.view.window().project_data()

			print(item)
			
			if item == 0:
				projectData['sass_debug'] = True;
				self.view.set_status('codekit', 'Debug On')
			else:
				projectData['sass_debug'] = False;
				self.view.set_status('codekit', 'Debug Off')

			self.view.window().set_project_data(projectData)


class refresh_browsers(sublime_plugin.TextCommand):
	def run(self, args, activate_browser=True,
			browser_name='all', auto_save=True, delay=None):

		print('Refreshing Browsers')

		# Auto-save
		if auto_save and self.view and self.view.is_dirty():
			self.view.run_command('save')

		# Detect OS and import
		if _os == 'Darwin':
			from mac import MacBrowserRefresh
			from mac.utils import running_browsers
			refresher = MacBrowserRefresh(activate_browser, running_browsers())
		elif _os == 'Windows':
			from win import WinBrowserRefresh
			refresher = WinBrowserRefresh(activate_browser)
		else:
			sublime.error_message('Your operating system is not supported')

		# Delay refresh
		if delay is not None:
			import time
			time.sleep(delay)

		# Actually refresh browsers
		if browser_name == 'Google Chrome':
			refresher.chrome()

		elif browser_name == 'Google Chrome Canary' and _os == 'Darwin':
			refresher.canary()

		elif browser_name == 'Safari':
			refresher.safari()

		elif browser_name == 'WebKit' and _os == 'Darwin':
			refresher.webkit()

		elif browser_name == 'Firefox':
			refresher.firefox()

		elif browser_name == 'Opera':
			refresher.opera()

		elif browser_name == 'IE' and _os == 'Windows':
			refresher.ie()

		elif browser_name == 'Iron' and _os == 'Windows':
			refresher.iron()

		elif browser_name == 'all':
			refresher.chrome()
			refresher.safari()
			refresher.firefox()
			refresher.opera()

			if _os == 'Darwin':
				refresher.canary()
				refresher.webkit()

			if _os == 'Windows':
				refresher.ie()
				refresher.iron()
