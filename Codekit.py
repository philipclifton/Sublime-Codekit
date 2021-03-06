import sublime_plugin
import subprocess
import sublime
import platform
import pprint
import os
import sys
import re
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

		sass_fired = False

		if os.path.isfile(view.file_name()) and view.file_name().split('.')[-1] == 'scss' or os.path.isfile(view.file_name()) and view.file_name().split('.')[-1] == 'sass':

			# Get file information from window
			fileName = view.file_name().split('/')[-1]
			destinFileName = fileName[:-4] + 'css' 
			projectPath = view.window().folders()[0];

			print('Original File:' + fileName)

			# Check to see if compiling base scss
			try:
				if len(view.window().project_data()['folders'][0]['base_scss_file']) > 0:
					fileName = view.window().project_data()['folders'][0]['base_scss_file']
					destinFileName = fileName[:-4] + 'css' 
					x = 0
			except KeyError:
				x = 0			

			# Get the sass path from Project
			sassOrigin = projectPath + os.sep + view.window().project_data()['folders'][0]['sass_origin']
			sassOutput = projectPath + os.sep + view.window().project_data()['folders'][0]['sass_output']
			
			print('INPUT FILE: ' + sassOrigin + os.sep + fileName);
			print('INPUT FILE: ' + sassOutput + os.sep + destinFileName);

			if os.path.isfile(sassOrigin + os.sep + fileName) and os.path.isfile(sassOutput + os.sep + destinFileName):

				# Command to run
				try:
					if view.window().project_data()['sass_debug'] is True:
						cmd = "sass --style compact --debug-info --no-cache '{0}':'{1}' ".format(sassOrigin + os.sep + fileName, sassOutput + os.sep + destinFileName)
					else:
						cmd = "sass --style compact --no-cache '{0}':'{1}' ".format(sassOrigin + os.sep + fileName, sassOutput + os.sep + destinFileName)
				except KeyError:
					cmd = "sass --style compact --no-cache '{0}':'{1}' ".format(sassOrigin + os.sep + fileName, sassOutput + os.sep + destinFileName)

				# Output the run command
				print('SASS COMMAND : ' + cmd) 

				# Run Command
				try:
					if view.window().project_data()['sass_compiler_active'] is False:
						x = None
					else:
						output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
						out, err = output.communicate()
						sass_fired = True;
						view.set_status('codekit', 'Sass compiled')	
						if out:
							self.debug_window(out.decode('utf-8'), view)
						if err:
							self.debug_window(err.decode('utf-8'), view)
				except KeyError:
					output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
					out, err = output.communicate()
					sass_fired = True;
					view.set_status('codekit', 'Sass compiled')	
					if out:
						self.debug_window(out.decode('utf-8'), view)
					if err:
						self.debug_window(err.decode('utf-8'), view)

			else:
				view.set_status('codekit', 'Sass project set incorrectly')

		else:
			view.set_status('codekit', 'File path incorrect')

		# Refresh Browser
		try:
			if view.window().project_data()['sass_browser_refresh'] is None:
				x = 0
			else:
				if view.window().project_data()['sass_browser_refresh'] is True:
					if sass_fired == True:
						view.window().run_command('refresh_browsers_delay');
					else:
						view.window().run_command('refresh_browsers');
		except KeyError:
			x = None

	def debug_window(self, data, view):

		self.output_view = view.window().get_output_panel("log")
		self.output_view.set_read_only(False)
		
		self.output_view.set_syntax_file("Packages/Diff/Diff.tmLanguage")
		args = {
			'output': data,
			'clear': True
		}
		self.output_view.run_command('git_scratch_output', args)

		self.output_view.set_read_only(True)
		view.window().run_command("show_panel", {"panel": "output.log"})
		view.set_status('codekit', 'Sass failed to compile')


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
	def run(self, args, activate_browser=False,
			browser_name='all', auto_save=True, delay=0):

		print(args)

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


class refresh_browsers_delay(sublime_plugin.TextCommand):
	def run(self, args, activate_browser=False,
			browser_name='all', auto_save=True, delay=0):

		print(args)

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



class find_image_files(sublime_plugin.TextCommand):
	images = []
	def run(self, edit):
		import os.path
		projectDir = self.view.window().project_data()['folders'][0]['path']
		
		if _os == 'Windows':
			try:
				if self.view.window().project_data()['follow_symlinks'] is True:
						from os.path import expanduser
						home = expanduser("~");
						projectDir = os.path.join(home, projectDir)
				else:
						projectDir = projectDir[2:]
			except KeyError:
				projectDir = projectDir[2:]
				
		for root, dirs, files in os.walk(projectDir):
			for f in files:
				fullpath = os.path.join(root, f)
				if os.path.splitext(fullpath)[1] == '.png' or os.path.splitext(fullpath)[1] == '.jpg' or os.path.splitext(fullpath)[1] == '.gif' or os.path.splitext(fullpath)[1] == '.svg':
					self.images.append(fullpath.replace(projectDir, '').replace('\\','/'))

		self.view.window().show_quick_panel(self.images, self.on_done);

	def on_done(self, index):		
		if index > -1:
			print(self.view.window().project_data()['folders'][0]['path'])
			self.view.run_command('insert', {
			    'characters': self.images[index],
			    })


class get_rgba_fallback(sublime_plugin.TextCommand):
	imageUrl = ''
	def run(self, args):
		selection = self.view.sel()

		print(selection)

		for region in selection:
			for line in self.view.lines(region):
				
				line_content = self.view.substr(line)
				dimensions = re.findall('rgba\(([0-9]*),([0-9]*),([0-9]*),([0-9.]*)\)', line_content ,re.DOTALL)
				
				passed = True

				try:
					dimensions[0][0]
					dimensions[0][1]
					dimensions[0][2]
					dimensions[0][3]
				except IndexError:
					passed = False
					print('Error finding required param')

				if passed == True:
					self.imageUrl = "http://rgbapng.com/?rgba={0},{1},{2},{3}".format(dimensions[0][0],dimensions[0][1],dimensions[0][2],dimensions[0][3]);
					self.view.window().show_input_panel('File Name: ', self.view.window().project_data()['folders'][0]['path'], self.file_done, self.file_ignore, self.file_ignore)

	def file_done(self, string):
		import urllib.request
		urllib.request.urlretrieve(self.imageUrl, string)

	def file_ignore(self, string):
		return ''


class mysql_kit(sublime_plugin.TextCommand):
	databases = [];
	tables = [];
	selected_database = 0;
	selected_table = 0;

	def run(self, args):
		s = sublime.load_settings('Codekit.sublime-settings');

		command = s.get('mysql_bin') + "mysql -e 'show databases' -u {0} -p{1}".format(s.get('mysql_user'), s.get('mysql_pass'));

		output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		out, err = output.communicate()

		self.databases = [];

		if out:

			self.databases = out.decode('utf-8').split('\n');

		if err:
			print(err.decode('utf-8'))

		self.view.window().show_quick_panel(self.databases, self.on_done_database);

	def on_done_database(self, index):
		self.selected_database = self.databases[index];

		s = sublime.load_settings('Codekit.sublime-settings');

		command = s.get('mysql_bin') + "mysql -e 'show tables from {2}' -u {0} -p{1}".format(s.get('mysql_user'), s.get('mysql_pass'), self.selected_database);

		output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		out, err = output.communicate()

		self.tables = [];

		if out:

			self.tables = out.decode('utf-8').split('\n');

		if err:
			print(err.decode('utf-8'))

		sublime.set_timeout(lambda: self.view.window().show_quick_panel(self.tables, self.on_done_table), 10)


	def on_done_table(self, index):
		self.selected_table = self.tables[index];

		s = sublime.load_settings('Codekit.sublime-settings');

		command = s.get('mysql_bin') + "mysql -e 'show columns from {2}.{3}' --raw -u {0} -p{1}".format(s.get('mysql_user'), s.get('mysql_pass'), self.selected_database, self.selected_table);

		output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		out, err = output.communicate()

		self.tables = [];

		if out:

			self.debug_window(out.decode('iso8859-1'), self.view)

		if err:
			print(err.decode('utf-8'))


	def debug_window(self, data, view):

		self.output_view = view.window().get_output_panel("log")
		self.output_view.set_read_only(False)
		
		self.output_view.set_syntax_file("Packages/Diff/Diff.tmLanguage")
		args = {
			'output': data,
			'clear': True
		}
		self.output_view.run_command('git_scratch_output', args)

		self.output_view.set_read_only(True)
		view.window().run_command("show_panel", {"panel": "output.log"})
		view.set_status('codekit', 'Sass failed to compile')





class dump_mysql(sublime_plugin.TextCommand):

	databases = [];
	selected_index = 0;

	def run(self, args):
		s = sublime.load_settings('Codekit.sublime-settings');

		command = s.get('mysql_bin') + "mysql -e 'show databases' -u {0} -p{1}".format(s.get('mysql_user'), s.get('mysql_pass'));

		output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		out, err = output.communicate()

		self.databases = [];

		if out:

			self.databases = out.decode('utf-8').split('\n');

		if err:
			print(err.decode('utf-8'))

		self.view.window().show_quick_panel(self.databases, self.on_done);

	def on_done(self, index):		
		if index > -1:

			from time import gmtime, strftime
			s = sublime.load_settings('Codekit.sublime-settings');

			self.selected_index = index;

			path = self.view.window().project_data()['folders'][0]['path'] + "/{0}/{1}-{2}.sql".format(s.get('mysql_project_folder'), self.databases[index], str(strftime('%d-%m-%y---%H-%M')));
			self.selected_index = index;
			self.view.window().show_input_panel('Save Database as: ', path, self.dump_database, False, False)

	def dump_database(self, value):
		s = sublime.load_settings('Codekit.sublime-settings');
		command = s.get('mysql_bin') + "mysqldump '{3}' > '{2}' -u {0} -p{1}".format(s.get('mysql_user'), s.get('mysql_pass'), value, self.databases[self.selected_index]);

		# print(command)

		output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		out, err = output.communicate()

		self.selected_index = False;

		if out:
			print(out.decode('utf-8'))
		if err:
			print(err.decode('utf-8'))
			



