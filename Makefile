ifeq ($(ANSIBLE_INVENTORY),)
$(error ansible inventory not found)
endif

all: deploy

deploy:
	cd ./jekyll/ && jekyll build
	ansible-playbook ansible-basicinside.de.yml

clean:
	cd ./jekyll/ && jekyll clean

.PHONY: all clean deploy
