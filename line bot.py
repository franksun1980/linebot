Skip to content
 
Search�K
All gists
GitHub
New gist
@franksun1980
  Star 2
  Fork 1
  @ctosibctosib/LinebotWithGoogle.py
Last active 3 months ago
Embed  
<script src="https://gist.github.com/ctosib/07eaa8f6ac385b3d28309f451e75f200.js"></script>
  Download ZIP
 Code  Revisions 4  Stars 2  Forks 1
�NLinebot�PGoogle sheet API�����X�A�s�@�O�b�����H
Raw
 LinebotWithGoogle.py
#encoding=UTF-8
"""
Author:Ethan Yang
Datetime:2016/12/29
Purpose:
1.��ܬO�g��?!
2.�Q��Line��@��J���O�����f�C
3.�O�b�C
4.�d�߳�r
"""
from flask import Flask,request
import requests
import json
import re
from bs4 import BeautifulSoup as bs
import time
#from linebot import LineBotApi
#from linebot.models import TextSendMessage
"""
��J�d�ҡGD apple �άO d apple
"""
def gettotal():
	
	apikey=AIzaSyC_sqVsyJBNoFiT7lwKQGvGPS77TtTrYoo
	getvalueurl='https://sheets.googleapis.com/v4/spreadsheets/1FHqzuHu3MSJU-8rvPznMgDMYVWoFIzMubEutKt7A01Q/values/sheet1!A:C?key=%s' % AIzaSyC_sqVsyJBNoFiT7lwKQGvGPS77TtTrYoo
	res = requests.get(getvalueurl)
	data = res.content
	
	jsondata = json.loads(data)
	values = jsondata['values']
    #�}��	
    count=0
    #�H�U3���ܼƧ@���[�`���ɭԥΪ� 	
    cash=0
	credit=0
	other=0
	for i in values:
		if count==0:
			count+=1
			continue
		else:
			#1�N��cash
			if i[2]=='cash':
				cash+=int(i[1])
			#2�N��credit
			elif i[2]=='credit':
				credit+=int(i[1])
			else:
				other+=int(i[1])
	outputvalue = 'Cash:{}, Credit:{}, \nOther:{}, Total:{}'.format(cash,credit,other,cash+credit+other)
	return outputvalue
"""
��ggoogle���A�i��O�b���ʧ@
�d�ҡG1000,1,note ��1�ӰѼƬ����B�A��2�Ӭ������G1���cash�B2���credit�B��L��other�A��3�ӰѼƬ��Ƶ��C
"""
def editRecord(accountlist):
	actionurl = 'https://docs.google.com/forms/d/e/1FHqzuHu3MSJU-8rvPznMgDMYVWoFIzMubEutKt7A01Q/formResponse'
	formurl = 'https://docs.google.com/forms/d/e/1FHqzuHu3MSJU-8rvPznMgDMYVWoFIzMubEutKt7A01Q/viewform'
	r = requests.Session()
	res = r.get(formurl)
	soup = bs(res.content,'html.parser')
	inputlist = soup.find_all('input')
	textarealist = soup.find_all('textarea')
	test={}
	for i in inputlist:
		#print i['aria-label']+':'+i['value']
		try:
			if i['aria-label']=='���B'.decode("utf-8"):
				test.update({i['name']:accountlist[0]})
			elif i['aria-label']=='����'.decode('utf-8'):
				if accountlist[1]=='1':
					inputkind = 'cash'
				elif accountlist[1]=='2':
					inputkind = 'credit'
				else:
					inputkind = 'other'
				test.update({i['name']:inputkind})
		except:
			test.update({i['name']:i['value']})
    #�]���������Ƶ���줣�O�������A�ҥH�b�O�b���ɭԡA�o�ӳ����i���i�L�A�ҥH�ݭn�P�_�A����J���ܤ~��J�C		
    if len(accountlist)==3:	
		for j in textarealist:
			#print j['name']+':'+j['value']
			test.update({j['name']:accountlist[2]})
	res = r.post(actionurl,data=test)
	return res.status_code

app = Flask(__name__)

@app.route("/",methods=["GET"])
def index():
	return "hello world",200
	
@app.route("/callback",methods=["POST"])
def index2():
	temp = request.get_json()
	for i in temp['events']:
		ttt =  i['replyToken']
		print i['source']['userId']
		if i['message']['type']=='text':
			msg = i['message']['text']
		replyapi(ttt,msg)
	return "hello world",200
	
def replyapi(accesstoken,msg):
	channeltoken=1513650586
	t = msg.encode('utf-8')
	inputlist = t.split(' ')
	count=0
	mat=[]
	if len(inputlist)>1:
		if inputlist[0]=='d' or inputlist[0]=='D':
			count,mat,outputstring = searchdictionary(count,inputlist)
	else:
		accountlist = inputlist[0].split(',')
		if inputlist[0]=='l' or inputlist[0]=='L':
			#�i��O���d�ߪ��ʧ@
			outputstring = gettotal()
			count=1
		elif len(accountlist)>1:
			#�i��O�b���ʧ@
			if editRecord(accountlist)==200:
				time.sleep(1)
				outputstring = '�������\'
				count=1
			else:
				outputstring = '��������'
				count=1
			#print 'hello'
		else:
			pat = re.compile(r".*(�T�T).*")
			print type(msg)
			mat = pat.findall(t)
	
	if len(mat)==0:
		if count==1:
			data={
			'replyToken':accesstoken,
			'messages':[{'type':'text','text':outputstring}]
			}
		else:
			data={
			'replyToken':accesstoken,
			'messages':[{'type':'text','text':'�Ӫ��D�F'},{'type':'text','text':'�i�H�h�U�F'}]
			}
	else:
		data={
		'replyToken':accesstoken,
		'messages':[{'type':'text','text':'�C�����e'}]
		}
	
	
	
	headers={
		'Content-Type':'application/json',
		'Authorization':'Bearer '+channeltoken
	}
	urladdress = 'https://api.line.me/v2/bot/message/reply'
	datajson = json.dumps(data)
	#print type(datajson)
	res = requests.post(urladdress,headers=headers,data=datajson)
	print res.status_code
	

if __name__=='__main__':
	app.run()