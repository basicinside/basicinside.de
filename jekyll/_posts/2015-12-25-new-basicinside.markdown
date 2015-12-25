---
layout: post
title:  "How I made the static html of basicinside.de more dynamic using
Jekyll."
date:   2015-12-25 09:24:44 +0100
categories: update
---

[Jekyll][jekyll] is a Ruby application. It generates html static sites based on dynamic content. You can write blog posts using the markdown markup language or nearly any other templating language.

A static site generated with Jekyll can easily be hosted as a github page. This saves precious hosting costs, but you have rely on github being reachable and not suffering from any DDos attack.

I used an ansible recipe to automatically deploy my static page in the past already. To deploy the Jekyll generated content, I just need change the source folder.

This is my ansible recipe to deploy the code:

{% highlight yaml %}
- hosts: basicinside.de
  sudo: yes
  vars:
   - docroot: /var/www/
  tasks:
   - name: Install Apache2
     apt: pkg=apache2 state=installed update_cache=true
     register: apache2_installed

   - name: Create Web Root
     when: apache2_installed|success
     file: dest="{{ docroot }}" mode=775 state=directory owner=www-data group=www-data
     register: webroot_installed

   - name: Sync Web Root
     when: webroot_installed|success
     sudo: no
     synchronize: src="./jekyll/_site/" dest="{{ docroot}}" rsync_path="sudo rsync"
{% endhighlight %}

You can find the most recent version on the [basicinside.de github
repo][basicinside.de-gh].

[jekyll]: http://jekyllrb.com
[basicinside.de-gh]:   https://github.com/basicinside/basicinside.de
