# leoslackbot
Leo is a Slack bot that utilizes Google's URL shortening and AWS's SNS services. Leo is programmed to send SMS alerts each time a target user posts a weblink. SMS shall contain a shortened URL of the same link.

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
![Imgur](https://i.imgur.com/eOXyCgJ.png "Screenshot 2")

