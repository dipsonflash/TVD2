import lirc
import xmltv
from datetime import datetime, timedelta
import pprint
from collections import defaultdict 
import pyttsx3
import urllib.request

POLL_TIME = 12 #Time in hours after which to pull new listings

class TvListings:
    def __init__(self):
        self.channelsCare = {'BBC One Yorks', 'BBC Two Eng', 'ITV', 'Channel 4', 'Channel 5'}
        #channelsCare = {'BBC One Yorks', 'BBC Two Eng', 'ITV', 'Film4'}
        self.lastUpdatedListings = datetime.now() - timedelta(hours=POLL_TIME)
        self.currentProgrammes = defaultdict(list)
        self.nextProgrammes = defaultdict(list)
        self.channelsInputDict = {}
        

    def Update_Listings(self):
        # Download the file from `url` and save it locally under `file_name`:        
        # urllib.request.urlretrieve("http://www.xmltv.co.uk/feed/6721", "tvlistings.xml")
        self.channelsInputDict = xmltv.read_channels(open('tvlistings.xml', 'r'))
        self.programmeInputDict = xmltv.read_programmes(open('tvlistings.xml', 'r'))
        self.lastUpdatedListings = datetime.now()
    
    def Retrieve_Listings(self):
        
        nowTime = datetime.now()
        if (nowTime - self.lastUpdatedListings) >= timedelta(minutes=POLL_TIME):
            self.Update_Listings()
        date_object = nowTime.strftime('%Y%m%d%H%S') + '00'
    
        # Print channels
        channelsDict = {}
        for i in self.channelsInputDict:
            channelsDict[i['id']] = i['display-name'][0][0]
        

        currentDictList = defaultdict(list)
        nextDictList = defaultdict(list)
            
        for programme in self.programmeInputDict:
            if channelsDict[programme['channel']] in self.channelsCare:
                if(int(programme['start'].split(' ')[0]) < int(date_object)):
                    currentDictList[programme['channel']].append(programme)
                else:
                    nextDictList[programme['channel']].append(programme)
        
        currentProgrammes = defaultdict(list)
        nextProgrammes = defaultdict(list)
        
        for channel in currentDictList:
           currentProgrammes[channelsDict[channel]] = max(currentDictList[channel], key = lambda programme: programme['start'])
           
        for channel in nextDictList:
           nextProgrammes[channelsDict[channel]] = min(nextDictList[channel], key = lambda programme: programme['start'])
        

        return(currentProgrammes, nextProgrammes)


if __name__ == '__main__':

    guide = TvListings()
    currentProgrammes, nextProgrammes = guide.Retrieve_Listings()
    sockid = lirc.init("myprogram")

    channel = 1
    numberToChannels = {1:'BBC One Yorks', 2:'BBC Two Eng', 3:'ITV', 4:'Channel 4', 5:'Channel 5'}
    print('READY')
    engine = pyttsx3.init()
    engine.setProperty('rate', 240)

    while(True):
        x = lirc.nextcode()
        if(len(x) > 0):
            if (x[0] == 'KEY_PAGEDOWN'):
                channel -= 1
                if (channel == 0):
                    channel = 5
            elif (x[0] == 'KEY_PAGEUP'):
                channel += 1
                if (channel == 6):
                    channel = 1
            elif(x[0] == 'KEY_1'):
                channel = 1
            elif(x[0] == 'KEY_2'):
                channel = 2
            elif(x[0] == 'KEY_3'):
                channel = 3
            elif(x[0] == 'KEY_4'):
                channel = 4
            elif(x[0] == 'KEY_5'):
                channel = 5
            
            curChannel = numberToChannels[channel]          
            engine.say(curChannel)
            engine.say('Currently')
            engine.say(currentProgrammes[curChannel]['title'][0][0])
            engine.say(currentProgrammes[curChannel]['desc'][0][0])            
            engine.say('Next')
            engine.say(nextProgrammes[curChannel]['title'][0][0])
            engine.say(nextProgrammes[curChannel]['desc'][0][0])
            engine.runAndWait()

    lirc.deinit()
