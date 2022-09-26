import requests, os
import telebot
import time, datetime
    
bot = telebot.TeleBot(str(os.environ['TELETOKEN']))
print (os.environ['TELETOKEN'])
user_id = str(os.environ['TELEID'])
print (user_id)
url='https://api.real-debrid.com/rest/1.0/'
apitoken=str(os.environ['RDTOKEN'])
print (apitoken)
headers = {'Authorization': f'Bearer {apitoken}'}

def add_magnet (magnet):
    data = {'magnet':magnet, 'hoster':'rd'}
    resp = requests.post(url+'torrents/addMagnet', data = data, headers = headers)
    id = resp.json()['id']
    resp = requests.post(url+'torrents/selectFiles/'+id, data = {'files':'all'}, headers = headers)
    return resp

def add_torrent (torrent_file):
    resp = requests.put(url+'torrents/addTorrent', data = torrent_file, headers = headers)
    id = resp.json()['id']
    resp = requests.post(url+'torrents/selectFiles/'+id, data = {'files':'all'}, headers = headers)
    return resp

def list_downloads (method):
    data = {'offset': 0, 'page':0, 'limit': 100, 'filter': 'downloaded'}
    r = requests.get('https://api.real-debrid.com/rest/1.0/torrents', data = data, headers = headers)
    links = list()
    linkdata = r.json()
    for t in linkdata:
        if (t['status']=='downloaded' and method=="downloaded"):
            links.append ('* '+t['filename'] +' ['+t['status']+'] ['+str(t['progress'])+']')
            continue
        if (method=='all'):
            links.append ('* '+t['filename'] +' ['+t['status']+'] ['+str(t['progress'])+']')
            continue
        if ((t['status']!='downloaded' and method=='loading')):
            links.append ('* '+t['filename'] +' ['+t['status']+'] ['+str(t['progress'])+']')
            continue

    msg = ''
    for t in links:
        msg=msg+t+'\n'
    return msg

@bot.message_handler(content_types=["text"])
def main(message):
    print (str(datetime.datetime.now())+' Income text message from: '+str(message.chat.id))
    if (user_id == str(message.chat.id)): 
        print ('Authorization completed')
        comand = message.text
        if ('magnet:' in message.text):
            print ('mmagnet incoming')
            res = str(add_magnet(comand))
            if (res.status_code==204):
                bot.send_message(message.chat.id, "Sucessfully added")
            else:
                bot.send_message(message.chat.id, "Error")
        if ('list' in message.text.lower()):
            print ('request for list')
            r = list_downloads ('all')
            bot.send_message(message.chat.id, str(r))
        if ('load' in message.text.lower()):
            print ('request for load')
            r= list_downloads ('loading')
            bot.send_message(message.chat.id, str(r))
        if ('done' in message.text.lower()):
            print ('request for downloaded') 
            r = list_downloads ('downloaded')
            bot.send_message(message.chat.id, str(r))
        

@bot.message_handler(content_types=["document"])
def main(message):
    print (str(datetime.datetime.now())+' Income document from: '+str(message.chat.id))
    if (user_id == str(message.chat.id)):
        if ('.torrent' in str(message.document.file_name)):
            print ('torrent incoming')
            file_name = message.document.file_name
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            res = add_torrent(downloaded_file)
            if (res.status_code==204):
                bot.send_message(message.chat.id, "Sucessfully added")
            else:
                bot.send_message(message.chat.id, "Error") 

if __name__ == '__main__':
    print ('Endpoint main')
    while True:
        try:
            print ('Starting polling')
            bot.polling(none_stop=True)
            print ('Polling cycle')
        except Exception as e:
            time = str(datetime.datetime.now())
            msg = f'{time}\tException: {str(e)}'
            print (msg)
            time.sleep(10)
