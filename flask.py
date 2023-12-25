import asyncio
import logging
from tqdm import tqdm
from telethon import TelegramClient, events, errors
from telethon.tl.types import PeerChannel, DocumentAttributeFilename, DocumentAttributeVideo, MessageMediaPhoto, PhotoSizeProgressive
from decouple import config
from telethon.sessions import StringSession
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filename='logfile.log',
)
logging.getLogger("pyrogram").setLevel(logging.DEBUG)

#logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
#level=logging.DEBUG)

#logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, filename='logfile.log')
logger = logging. getLogger(__name__)
queue = asyncio. Queue()

APP_ID = config("APP_ID", default=None, cast=int)
API_HASH = config("API_HASH", default=None)
SESSION = config("SESSION")
CHAT_LIST = config("CHAT_LIST")

client = TelegramClient(StringSession(SESSION), APP_ID, API_HASH)
SESSION = client.session.save()
#with TelegramClient('viperdupes', APP_ID, API_HASH) as client:
     #print(client.session.save())
CHAT_LIST = ['https://t.me/+ARvYdn7lqJN']  

# calculate file size
def convert_size(text):
     units = ["B", "KB", "MB", "GB", "TB", "PB"]
     size = 1024
     for i in range(len(units)):
         if (text/size) < 1:
             return "%.2f%s" % (text, units[i])
         text = text/size
     return 0

# Get file information
def get_file_information(message):
     file = None
     if message.media is not None:
         try:
             if type(message.media) is MessageMediaPhoto:
                 photo = message.media.photo
                 file = {
                     'id': photo.id,
                     'access_hash': photo.access_hash,
                     'type': 'photo',
                     'datetime': photo.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
                 }
                 for i in photo. sizes:
                     if type(i) is PhotoSizeProgressive: # file name
                         file["size"] = i.sizes[len(i.sizes)-1] # movie name
                         file["w"] = i.w # movie width
                         file["h"] = i.h # movie height
             else:
                 document = message.media.document
                 file = {
                     'id': document.id,
                     'access_hash': document. access_hash,
                     'type': document.mime_type, # file type
                     'size': document.size, # file size
                     'datetime': document.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
                 }
                 for i in document.attributes:
                     if type(i) is DocumentAttributeFilename: # file name
                         file["name"] = i.file_name # movie name
                     if type(i) is DocumentAttributeVideo: # Video resolution
                         file["w"] = i.w # movie width
                         file["h"] = i.h # movie height
         except:
             print("An error occurred")
             print(message)
             return None
        
     return file

# Check if the same file id exists
def check_duplicate_file(message, entity):
     file = get_file_information(message)
     if file is None: return False, file
     if file['id'] in file_list[entity.id]:
         return True, file
     file_list[entity.id].append(file['id'])

     return False, file

file_list = {} # record file id

@events.register(events.NewMessage(chats=tuple(CHAT_LIST)))
async def handler(update):
     # get group new information
     chat_id = update.message.to_id
     try:
         entity = await client.get_entity(chat_id)
     except ValueError:
         entity = await client.get_entity(PeerChannel(chat_id))
     except Exception as e:
         logger. error(type(e.__class__, e))
         return

     text = ""
     print("Group:{}, new message".format(entity.title))
     is_duplicate, file = check_duplicate_file(update.message, entity)
     if is_duplicate:
         text += "time:{}".format(file['datetime'])
         if 'type' in file: text += ", file type: {}".format(file['type'])
         if 'name' in file:text += ", file name:{}".format(file['name'])
         text += ", file size:{}".format(convert_size(file['size']))
         if 'w' in file and 'h' in file:
             text += ", resolution:{}x{}".format(file['w'],file['h'])
         print(text)
         await client.delete_messages(entity=entity, message_ids=[update.message.id]) # delete message
            

async def init():
     bar = tqdm(CHAT_LIST)
     for i in bar:
         entity = await client.get_entity(i)
         file_list[entity.id] = [] # Initialize each group file list
         total = 0 # count the number of messages processed
         delete = 0 # Count the number of deleted messages

         # Read group messages (from old to new)
         async for message in client.iter_messages(entity, reverse = True):
             is_duplicate, _ = check_duplicate_file(message, entity)
             if is_duplicate:
                 print('Group:{}, delete duplicate files[{}]'.format(entity.title,message.id))
                 await client.delete_messages(entity=entity, message_ids=[message.id]) # delete message
                 delete += 1
             total += 1
             bar.set_description('Group: {} Initialize check for duplicate files, check quantity: {}, delete: {}'.format(entity.title, total, delete))
        
     return False
with client:
     print("Initialize check for duplicate files")
     client.loop.run_until_complete(init())
     
     print("Start listening for new messages:")
     client.add_event_handler(handler)
     client.run_until_disconnected()

#if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8080, debug=True)
