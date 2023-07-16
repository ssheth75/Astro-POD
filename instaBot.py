from instabot import Bot 
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import creds
import processImage
import shutil
import os
import re



### Delete config file from directory to prevent future login issues ###
config_folder = ''

# Remove the config folder if it exists
if os.path.exists(config_folder):
    shutil.rmtree(config_folder)




### Get image from NASA ###
url = "https://apod.nasa.gov/apod/astropix.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

image = soup.find("img")
imageSrc = image["src"]

# Check if the imageSrc URL has a scheme and add it if missing
if not imageSrc.startswith('http'):
    imageSrc = urljoin(url, imageSrc)

response = requests.get(imageSrc)
with open("post.jpg", "wb") as file:
    file.write(response.content)




### Crop or resize the image for compatibility with Instagram ###
inputImagePath = "post.jpg"
outputImagePath = "formattedPost.jpg"
targetSize = 1080
processImage.cropOrResizeimage(inputImagePath, outputImagePath, targetSize)




### Obtain Image title and credits ###
imageTitle = ""
credits = []
centerTags = soup.find_all("center")

if len(centerTags) >= 2:
    targetCenterTag = centerTags[1]
    imageTitle = targetCenterTag.find("b").text
    print(imageTitle)

    # Obtain the credits
    targetATags = targetCenterTag.find_all("a")

    for targetATag in targetATags:
        credits.append(targetATag.text)
    print(credits)

else:
    print("Image title not found.")
    exit(1)

formattedImageTitle = imageTitle.lstrip()




### Obtain the image description from NASA ###
paragraphs = soup.find_all("p")
formattedText = ""

targetOccurences = None
pattern = re.compile(r"Explanation:(.*?)Tomorrow's picture:", re.DOTALL)
for paragraph in paragraphs:
    match = pattern.search(paragraph.text)
    if match:
        targetOccurences = paragraph
        break

if targetOccurences:
    text = match.group(1).strip()

    # Remove newlines and extra spaces after periods
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.\s+", ". ", text)

    formattedText = text.replace('\xa0', ' ')
else:
    print("Target paragraph not found.")
    exit(1)




### Format Caption ###
currentDate = datetime.now().strftime("%m/%d/%Y")

creditsString = ""
if len(credits) > 0:
    creditsString = ", ".join(credits)
    print(creditsString)
else:
    creditsString = "NASA"

formattedCaption = "ASTRO Picture of The Day: " + currentDate + "\n\n" + formattedImageTitle + "\n\n" + formattedText + "\n\n" + "Image Credit & Copyright: NASA, " + creditsString
print(formattedCaption)




### Login to Instagram ###
bot = Bot()
bot.login(username=creds.username, password=creds.password)

# Make the post
bot.upload_photo("formattedPost.jpg", caption=formattedCaption)
print("Post successful!")
