ifeq ($(ANSIBLE_INVENTORY),)
$(error ansible inventory not found)
endif

all: deploy

deploy:
	evernote-sync/env/bin/python evernote-sync/sync.py
	cd ./jekyll/ && jekyll build
	ansible-playbook ansible-basicinside.de.yml

clean:
	cd ./jekyll/ && jekyll clean

.PHONY: all clean deploy
