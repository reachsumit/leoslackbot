import os,time,random
from slackclient import SlackClient
import re
from pyshorteners import Shortener
import boto3
import ssl

GOOGLE_KEY = os.environ.get('GOOGLE_KEY')
BOT_ID = os.environ.get('BOT_ID')
BOT_TAG = "<@"+str(BOT_ID)+">"
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

user_base = {}

PASSKEY = os.environ.get('MASTER_PASS')
MASTER_PHONE = os.environ.get('MASTER_PHONE')
follow = ""
smsBlocked = False

def send_message(msg,target):
    global smsBlocked,user_base,MASTER_PHONE
    print("Send sms to: "+target+" with content: "+msg)
    if smsBlocked:
        return None
    client = boto3.client('sns',region_name="us-east-1",aws_access_key_id=os.environ.get('AWS_KEY_ID'),aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'))
    if target == 'all':
        for user,phone in user_base.items():
            response = client.publish(
                PhoneNumber=phone,
                Message=msg
            )
            for k,v in response.items():
                print(k,v)
    elif target == 'master':
        response = client.publish(
            PhoneNumber=MASTER_PHONE,
            Message=msg
        )
        for k,v in response.items():
            print(k,v)

def is_private(output):
    global BOT_ID
    print("checking private. Channel: "+output['channel']+" user: "+output['user'])
    return (output['channel'].startswith('D')) and (output['user']!=BOT_ID)

def is_it_for_me(slack_rtm_output):
    global BOT_TAG
    forMe = False
    output_list = slack_rtm_output
    for output in output_list:
        if ('type' in output) and (output['type']=='message') and ('text' in output):
            print(output)
            if BOT_TAG in output['text']:
                print("Its for me in public from "+output['user'])
                forMe = True
            elif is_private(output):
                print("Its for me in private from "+output['user'])
                forMe = True
            if 'user' in output:
                checkOutcome = msg_received(output)
                if checkOutcome:
                    if send_message(checkOutcome,"all"):
                        print("SMS sent.")
        if ('subtype' in output) and (output['subtype']=='channel_join') and ('user' in output):
            if 'channel' in output:
                slack_client.api_call("chat.postMessage",channel=output['channel'],text="Hi <@"+output['user']+">, Welcome to the group. :blush:",as_user=True)
    return forMe, output

def is_hello(text):
    tokens = [word.lower() for word in text.strip().split()]
    return any(match in tokens for match in ['hi','hello','hey','bonjour','sup','hola','yo','namastey'])

def is_bye(text):
    tokens = [word.lower() for word in text.strip().split()]
    return any(match in tokens for match in ['bye','goodbye','revoir','adois','later','tata','cya'])

def say_hello(user):
    name = "<@"+user+">"
    response_template = random.choice(['Sup, '+name, 'Yo!', 'Hola, '+name, 'Bonjour!','Namastey!'])
    response_template += " :dog:"
    return response_template

def say_bye(user):
    name = "<@"+user+">"
    response_template = random.choice(['See you later, '+name, 'Adios amigo!', 'Bye, '+name, 'Alvida.'])
    return response_template

def has_add(text):
    match = ['add me','add my','subscribe me','subscribe my']
    for item in match:
        if re.search('(^|\s)'+item+'($|\s)',text.lower()) is not None:
            return True
    return False

def has_remove(text):
    match = ['remove me','remove my','delete me','delete my','unsubscribe me','unsubscribe my']
    for item in match:
        if re.search('(^|\s)'+item+'($|\s)',text.lower()) is not None:
            return True
    return False

def find_number(text):
    if not text:
        return None
    phoneNumRegex1 = re.compile(r'(\d\d\d)-(\d\d\d)-(\d\d\d\d)')
    mo = phoneNumRegex1.search(text)
    if not mo:
        phoneNumRegex2 = re.compile(r'\d\d\d\d\d\d\d\d\d\d')
        mo = phoneNumRegex2.search(text)
        if not mo:
            phoneNumRegex3 = re.compile(r'(\d\d\d)-(\d\d\d\d\d\d\d)')
            mo = phoneNumRegex3.search(text)
            if not mo:
                return None
            else:
                return mo.group(1)+mo.group(2)
        else:
            return mo.group()
    return mo.group(1)+mo.group(2)+mo.group(3)

def has_manual(text):
    if 'manual' in text.lower():
        return True

def admin_tasks(command):
    global smsBlocked,follow,user_base,slack_client,PASSKEY
    text = command['text']
    channel = command['channel']
    ret = None
    if PASSKEY in text:
        if 'add' in text:
            if "=" in text:
                follow = text.split("=")[1]
                ret = "updated person to follow"
            else:
                ret = "Couldn\'t udpate person to follow. Please check your syntax."
        elif 'remove' in text:
            ret = "removing person to follow"
            follow = ""
        elif 'show' in text:
            ret = "Currently following: <@"+follow+">"
        elif 'database' in text:
            ret = str(user_base)
        elif 'block' in text:
            if smsBlocked:
                smsBlocked = False
                ret="SMS service is now unblocked"
            else:
                smsBlocked = True
                ret="SMS service is now blocked"
    return ret

def msg_received(command):
    global GOOGLE_KEY,follow
    response = None
    if(command['user']==follow):
        print("message is from the person being followed")
        URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        regexp = re.compile(URL_REGEX)

        #test = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        #regexp = re.compile(test)
        output = regexp.findall(command['text'])
        if output:
            response = "Hi! Leo Here. New link(s): "
            for url in output:
                try:
                    s = Shortener('Google',api_key=GOOGLE_KEY)
                    short_url = s.short(url)
                    response += short_url + " "
                    print('short url is :'+short_url)
                    #print(s.shorten) # prints the short url
                    print('shortened from: '+s.expanded)
                except ssl.SSLError as err:
                    pass
        else:
            print("Couldn't parse the URL or no URL was present in the message")
    return response

def handle_command(command):
    global slack_client,user_base
    talked = False
    if is_hello(command['text']):
        response = say_hello(command['user'])
        talked = True
    elif is_bye(command['text']):
        response = say_bye(command['user'])
        talked = True
    if has_add(command['text']):
        response = "Hi <@"+command['user']+">, I understand that you want me to subscribe you. "
        number = None
        number =  find_number(command['text'])
        if number:
            user_base[command['user']] = number
            response += "\nI've added your number: +1-"+number+" to my system. :simple_smile:"
            send_message(command['user']+" with phone number "+number+" just subscribed to LeoSlackBot.","master")
        else:
            response += "\nBut I could not figure out your number. :no_mouth: Please use one of these formats: xxx-xxx-xxxx OR xxx-xxxxxxx OR xxxxxxxxxx to give me your 10-digit number."
        talked = True
    elif has_remove(command['text']):
        response = "Hi <@"+command['user']+">, I understand that you want me to un-subscribe you. "
        number = user_base.pop(command['user'],None)
        if number:
            response += "\nAnd I've removed your number: +1-"+number+" from my system. :simple_smile:"
        else:
            response += "\nBut I could not find your number in my system. :no_mouth:"
        talked = True
    elif has_manual(command['text']):
        response = """* To add your phone number. In a sentence tell me to add you or your number along with your 10-digit number in one of these formats: xxx-xxx-xxxx OR xxx-xxxxxxx or xxxxxxxxxx
* To remove your phone number from my system, tell me in a sentence to remove or unsubscribe you.
That's about it. """
        talked = True
    admin_update = admin_tasks(command)
    if admin_update:
        talked = True
        response = admin_update
    if talked == False:
        response = "<@"+command['user']+">, I'm not programmed to answer that."
    channel = command['channel']
    slack_client.api_call("chat.postMessage",channel=channel,text=response,as_user=True)

if __name__ == '__main__':
    READ_WEBSOCK_DELAY = 1
    mine = False
    if slack_client.rtm_connect():
        print("Leo connected and running!")
        while True:
            some_data = slack_client.rtm_read()
            if some_data and len(some_data) > 0:
                mine, command = is_it_for_me(some_data)
            if mine:
                handle_command(command)
            time.sleep(READ_WEBSOCK_DELAY)
    else:
        print("Connection failed. Invalid Slack token or Bot id.")
