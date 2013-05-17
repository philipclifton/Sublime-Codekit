# Sublime Codekit

## Features
- Sass/Scss compiler 
- Browser Refresh (All Major Osx & Windows)
- Debug switch
- Refresh on/off switch
- Compiler on/off switch
- Per-project settings

## Requirements 

You need sass installed

OSX:
```bash
gem install sass
```

Windows installer
http://rubyinstaller.org/downloads/



## Project Settings

Example Directories: 
```json
"folders":
	[
		{
			"path": "/Users/philipclifton/Projects/philipmclifton",
			"sass_origin": "static/scss",
			"sass_output": "static/css",
			"base_scss_file": "styles.scss"
		}
	]
```

### Debug On / Off

Open command pallet and search for `Project: SASS Debug`.
Option is appended to project settings file.

### Compiler On / Off
	
Open command pallet and search for `Project: SASS Compiler`.
Option is appended to project settings file.

### Browser Refresh On / Off
	
Open command pallet and search for `Project: Browser Refresh`.
Option is appended to project settings file.