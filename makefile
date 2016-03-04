install:
	python install.py
	mkdir -p ~/bin/
	cp forunit ~/bin/forunit
	chmod +x ~/bin/forunit
	export PATH=$$PATH:$$HOME/bin
