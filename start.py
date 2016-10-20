#!/usr/bin/env python

import web
from web import form
import youtubeup as yup
import argparse
import csv
from datetime import *
import threading
from tbaAPI import *
from time import sleep

render = web.template.render('webpage/')

dataform = form.Form(
	form.Dropdown("where",
		[("../","Parent Folder to Scripts"),("", "Same Folder as Scripts")],
		description="Match Files Location"),
	form.Dropdown("events",
		[],
		description="This Week's Events"),
	form.Textbox("prodteam", description="Production Team", size=41),
	form.Textbox("twit", description="Twitter Handle", size=41),
	form.Textbox("fb", description="Facebook Name", size=41),
	form.Textbox("web", description="Website Link", size=41),
	form.Textbox("ename", description="Event Name", size=41),
	form.Textbox("ecode", description="Event Code (ex. 2016arc)"),
	form.Textbox("ext", description="File Extension", size=41),
	form.Textbox("pID",
		form.regexp("^PL", "Must be a playlist ID, all of which start with 'PL'"),
		form.regexp("^\s*\S+\s*$", "Can not contain spaces."),
		description="Playlist ID",
		size=41),
	form.Textbox("tbaID",
		description="TBA Event ID",
		value="Contact 'contact@thebluealliance.com to get keys",
		size=41),
	form.Textbox("tbaSecret",
		description="TBA Event Secret",
		value="Contact 'contact@thebluealliance.com to get keys",
		size=41),
	form.Textarea("description",
		description="Video description",
		value="Add alternate description here."),
	form.Textbox("mnum",
		form.notnull,
		form.regexp("\d+", "Cannot contain letters"),
		form.Validator("Must be more than 0", lambda x:int(x)>0),
		description="Match Number"),
	form.Dropdown("mcode",
		[("qm", "Qualifications"), ("qf","Quarterfinals"), ("sf", "Semifinals"), ("f", "Finals")],
		description="Match Type"),
	form.Checkbox("tiebreak", description="Tiebreaker"),
	form.Checkbox("tba", checked=True, description="Use The Blue Alliance"),
	form.Textbox("end", 
		description="Last Match Number", 
		value="Only for batch uploads"),
		validators = [form.Validator("Last Match Number must be greater than Match Number", 
		lambda i: i.end == "Only for batch uploads" or int(i.end) > int(i.mnum))]
	)

class index(threading.Thread):
	def run(self):
		urls = ('/', 'index')
		app = web.application(urls, globals())
		app.run()

	def GET(self):
		form = dataform()
		events = get_events_of_the_week()
		for event in events:
			form.events.args.append((event['key'],event['name'].split("-")[0]))
		form.events.args.append(("","Other"))
		del form.events.args[0]
		with open('form_values.csv', 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='|')
			i = 0
			for row in reader:
				for value in row:
					if value is not "":
						switcher = {
							0: form.where,
							1: form.events,
							2: form.prodteam,
							3: form.twit,
							4: form.fb,
							5: form.web,
							6: form.ename,
							7: form.ecode,
							8: form.ext,
							9: form.pID,
							10: form.tbaID,
							11: form.tbaSecret,
							12: form.description,
							13: form.mnum,
							14: form.mcode,
							15: form.tiebreak,
							16: form.tba,
							17: form.end,
						}
						if i == 15 or i == 16 or i == 0:
							if value == "True": switcher[i].set_value(True)
							if value == "False": switcher[i].set_value(False)
						else : switcher[i].set_value(value)
					i = i + 1
				break
		return render.forms(form)

	def POST(self):
		form = dataform()
		if not form.validates():
			return render.forms(form)
		else:
			form.ecode.set_value(form.d.events)
			events = get_events_of_the_week()
			for event in events:
				if event['key'] == form.d.events:
					form.ename.set_value(event['name'].split("-")[0])
			then = datetime.now()
			reader = csv.reader(open('form_values.csv'))
			row = next(reader)
			parser = argparse.ArgumentParser(description='Upload videos to YouTube for FRC matches')
			args = parser.parse_args()
			formdata = web.input()
			args.then = then
			args.gui = True
			args.where = row[0] = form.d.where
			row[1] = form.d.events
			args.prodteam = row[2] = form.d.prodteam
			args.twit = row[3] = form.d.twit
			args.fb = row[4] = form.d.fb
			args.web = row[5] = form.d.web
			args.ename = row[6] = form.d.ename
			args.ecode = row[7] = form.d.ecode
			args.ext = row[8] = form.d.ext
			args.pID = row[9] = form.d.pID
			args.tbaID = row[10] = form.d.tbaID
			args.tbaSecret = row[11] = form.d.tbaSecret
			args.description = row[12] = form.d.description
			args.mnum = row[13] = int(form.d.mnum)
			args.mcode = row[14] = form.d.mcode
			args.tiebreak, row[15] = formdata.has_key('tiebreak'), str(formdata.has_key('tiebreak'))
			args.tba, row[16] = formdata.has_key('tba'), str(formdata.has_key('tba'))
			args.end = row[17] = form.d.end
			thr = threading.Thread(target=yup.init, args=(args,))
			thr.daemon = True
			thr.start()
			if form.d.end == "Only for batch uploads":
				form.mnum.set_value(str(int(form.d.mnum) + 1))
			else:
				form.mnum.set_value(str(int(form.d.end) + 1))
				form.end.set_value("Only for batch uploads")
			row[13] = int(form.d.mnum)
			row[17] = form.d.end
			writer = csv.writer(open('form_values.csv', 'w'))
			writer.writerow(row)
			return render.forms(form)

if __name__=="__main__":
	web.internalerror = web.debugerror
	t = index()
	t.daemon = True
	t.start()
	while True:
		sleep(100)