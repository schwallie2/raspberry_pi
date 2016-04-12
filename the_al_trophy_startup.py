import os
import gspread
# Must have a secret.py file with your credentials in it!
import secret
import glob
from oauth2client.client import SignedJwtAssertionCredentials
import socket
import traceback
from time import sleep
from tendo import singleton

# This makes sure we don't have multiple instances running
me = singleton.SingleInstance()
print 'No other instance running, starting looper'


def checknetwork():
    """
    Checks if we have a network connection
    :return:
    """
    ip = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        ip = s.getsockname()[0]
        s.close()
    except socket.error:
        return False
    else:
        return ip


def main():
    """
    Uses a quick loop to check the network connection
    :return:
    """
    success = checknetwork()
    ct = 1
    while not success and ct < 5:
        print "Waiting for connection..."
        success = checknetwork()
        sleep(3)
        ct += 1
    return success


# If Connection, go and look for new videos on the Google Sheet
connection = main()
if connection:
    try:
        # os.system('fbcp &')
        # Sign-in to Google, MUST HAVE SECRET.PY CREDENTIALS
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(secret.drive_details['client_email'],
                                                    secret.drive_details['private_key'], scope)
        gc = gspread.authorize(credentials)
        # The name of your google doc
        wks = gc.open("al")
        # Name of your worksheet
        wks = wks.worksheet("videos")
        recs = wks.get_all_records()
        # I gave a column header of Video URL
        col_header = 'Video URL'
        recs = [i[col_header] for i in recs]
        video_list = glob.glob('videos/*')
        for val in recs:
            print val
            print video_list
            if not any(val.split('=')[-1] in s for s in video_list):
                # Use youtube-dl to download the video
                os.system("youtube-dl -o 'videos/%%(title)s-%%(id)s.%%(ext)s\' %s" % val)
    except Exception:
        print traceback.format_exc()
        # Something wrong, continue on, need to alert the user to this
        # TODO: Alert admin
        pass
else:
    print 'No Connection!'
# Start Video Loop
ct = 1
video_list = glob.glob('videos/*')
os.system('fbcp &')
# It will eventually stop running! 300 is how many loops I did, you can make it while True to never stop
while ct < 300:
    ct += 1
    for val in video_list[::-1]:
        os.system('omxplayer "%s"' % val)
os.system('sudo killall fbcp')

__author__ = "Chase Schwalbach"
__credits__ = ["Chase Schwalbach"]
__version__ = "1.0"
__maintainer__ = "Chase Schwalbach"
__email__ = "chase.schwalbach@avant.com"
__status__ = "Production"
