ifeq ($(ANSIBLE_INVENTORY),)
$(error ansible inventory not found)
endif

all: check deploy

check:
	tidy ./docroot/*.html
	tidy ./docroot/notes/*.html

deploy:
	cd ./jekyll/ && jekyll build
	ansible-playbook ansible-basicinside.de.yml

.PHONY: all check deploy
