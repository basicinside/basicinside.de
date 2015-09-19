ifeq ($(ANSIBLE_INVENTORY),)
$(error ansible inventory not found)
endif

all: check deploy

check: 
	tidy ./docroot/*.html

deploy: 
	ansible-playbook ansible-basicinside.de.yml

.PHONY: all check deploy