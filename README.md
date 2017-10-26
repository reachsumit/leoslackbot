# leoslackbot
Leo is a Slack bot that utilizes Google's URL shortening and AWS's SNS services. Leo is programmed to send SMS alerts each time a target user posts a weblink. SMS shall contain a shortened URL of the same link.

## Supported operations
* People can talk with Leo in group chats with @leo tag and without any tag in personal chatrooms.
* Leo the bot can exchange greetings such as hi, hello, bye etc. 
* Leo looks for keywords such as "add me", "add my", "subscribe me" or "subscribe my" and then the 10-digit contact number in various supported formats to register a user for the services.
* To unsusbscirbe a user from service, Leo looks for keywords such as "delete me", "delete my", "remove me", "remove my", "unsubscribe me" or "unsubscribe my" in chats directed to Leo.
* Leo displays support manual if the sentence directed at Leo has "manual" (case is irrelevant) word in it.
* Leo greets all new incoming members in the group.
* __admin operations__ : With a passkey (password) Leo accepts commands that are supposed to be executed by administrator only (in one-to-one chat to keep the passkey secret). Following operations are supported for an admin:
     * List all the registered users (for receiving SMS updates)
     * View the target member
     * Change the target member
     * Block/Unblock (toggle) SMS sending operation

## Directory structure
* herokuApp/  
     * -- app.py : main python code that runs in loop at heroku server  
     * -- requirements.txt : specifies package dependencies to heroku server  
     * -- Procfile : required for heroku app  
 * puppy-icon.png : image used on Slack website to give a face to bot  

## Screenshots
### private chat
![Imgur](https://i.imgur.com/mSjxE4e.png "Screenshot 1")
### group chat
![Imgur](https://i.imgur.com/dg776pZ.png "Screenshot 2")
#### greeting new members
![Imgur](https://i.imgur.com/1z4PFJm.png "Screenshot 2")
