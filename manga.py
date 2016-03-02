#! /usr/bin/python3

import os, requests, sys, webbrowser, bs4, shelve, time
#from gi.repository import Notify
import notify2

while True:
	#    a list with the link of the manga page on mangafox.com
	try:
		manga_file_list = open('mangalist.txt').readlines()
	except:
		print('File name for the file containing manga links incorrect...')
		print('Exiting...')
		exit()


	#    a file to store the links of new chapters	
	link_file = open('linkfile.txt','w')


	#    a shelve file to store the chapter which is latest when running this script
	data_file = shelve.open('lastmangachapter')
	key = 'manga'
	try:
		manga_dict = data_file[key]
		print('key exists')
	except:
		manga_dict = {}
		data_file[key] = manga_dict
		print('key does not exist')


	#    initialize the notification 
	notify2.init('Manga')
	title = ('New Chapter Available')
	body = ''
	notification = notify2.Notification(
			title,
			body,
		)



	#    function to display the notification as well as store the link of the chapter in linkfile and chapter name in shelve file 
	def show_chapter_notification(link, body, title_string):
		link_file.write(link + '\n')
		manga_dict[title_string] = body
		notification.update(title, body)
		notification.show()

	counter = 0
	for links in manga_file_list:

		try:
			res = requests.get(links)
		except:
			print('link %s is invalid. Please check. Skipping for now...' %(counter))	
			continue;
		manga_page_html = bs4.BeautifulSoup(res.text)
		newchap_list = manga_page_html.find_all(class_='newch')
		title_name = manga_page_html.select('h1')
		title_string = ''	

		try:
			title_string = title_name[0].getText()
			print(title_string)
		except:	
			print('Cannot locate manga name. Site format must have changed. Check code')
			print('Exiting...')
			exit()

		print(manga_dict)

		#	in case a new manga has been added, one whose info is not present, 
		# 	the script will store either the first chapter in the list or the 	
		# 	latest chapter for the manga in the shelve file if title_string not in manga:

		if title_string not in manga_dict:		
			newchapter = manga_page_html.select('.newch')

			if len(newchap_list) == 0:
				chap = manga_page_html.select('.tips')# will return the tag for the first chapter in the list
				if len(chap) > 0:	
					body = chap[0].getText()
					link = chap[0].attrs['href']
					show_chapter_notification(link, body, title_string)
				else:
					print('No chapter found for this manga...')
			else:
				parent_tag = newchapter[0].parent# will return the h3 tag encompassing the new chapter
				tag = parent_tag.contents# will return all children of h3 tag
				title = "New Chapter Available"
				body = tag[1].getText()
				link = tag[1].attrs['href']
				show_chapter_notification(link, body, title_string)

		elif len(newchap_list) == 0:
			print('No New Chapter')
	
		else:
			newchapter = manga_page_html.select('.newch')
			parent_tag = newchapter[0].parent# will return the h3 tag encompassing the new chapter
			tag = parent_tag.contents# will return all children of h3 tag
			title = "New Chapter Available"
			body = tag[1].getText()
			link = tag[1].attrs['href']
	
			if manga_dict[title_string] != body: 
				manga_dict[title_string] = body
				show_chapter_notification(link, body, title_string)

	del data_file[key]
	data_file[key] = manga_dict
	data_file.close()
	link_file.close()

	#	check again after 4 hours
	time.sleep(60*60*4)

