import urllib2, urllib
import json
import cv2
import random
import time
import os

apiKey = "Insert Facebook API key here"
fields = urllib.urlencode(
    {
        "access_token": apiKey
    }
)
url = "https://graph.facebook.com/v2.3/me/photos?{0}".format(fields)

print "Requesting Data from: "; print url; print

request = urllib2.urlopen(urllib2.Request(url))
rawData = request.read()

data = json.loads(rawData)

for item in data['data']:
    for i in item['images']:
        downloadLocation = i['source']
        itemId = str(random.randint(1000000000,9999999999))
        pictureLocation = ("Pictures/{0}.jpg".format(itemId))
        try:
            pictureRequest = urllib.urlretrieve(downloadLocation, pictureLocation)
            print; print "Downloading From: "; print downloadLocation
            print "Downloading To: {0}".format(pictureLocation)
        except:
            print "Facebook rejected image: {0}".format(itemId)
        time.sleep(0.1)

        cascPath = "Additions/haarcascade_frontalface_default.xml"

        faceCascade = cv2.CascadeClassifier(cascPath)
        img = cv2.imread(pictureLocation)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        print "Found {0} faces!".format(len(faces))
        if len(faces) == 0:
            os.remove(pictureLocation)
        else:
            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imshow(itemId ,img)
            cv2.moveWindow(itemId, random.randint(0, 500), random.randint(0, 500))
            cv2.imwrite("ProcessedPictures/{0}.jpg".format(itemId), img)

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
    	break

cv2.destroyAllWindows()
