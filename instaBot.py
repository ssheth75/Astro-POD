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
# image = images[0]
image_src = image["src"]

# Check if the image_src URL has a scheme and add it if missing
if not image_src.startswith('http'):
    image_src = urljoin(url, image_src)

response = requests.get(image_src)
with open("post.jpg", "wb") as file:
    file.write(response.content)

### Crop or resize the image for compatibility with Instagram ###
inputImagePath = "post.jpg"
outputImagePath = "formattedPost.jpg"
targetSize = 1080
processImage.cropOrResizeimage(inputImagePath, outputImagePath, targetSize)

### Obtain Image title ###
imageTitle = ""
centerTags = soup.find_all("center")

if len(centerTags) >= 2:
    target_center_tag = centerTags[1]
    imageTitle = target_center_tag.find("b").text
    print(imageTitle)
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
    # print(formattedText)
else:
    print("Target paragraph not found.")
    exit(1)


### Format Caption ###
currentDate = datetime.now().strftime("%m/%d/%Y")
formattedCaption = "ASTRO Picture of The Day: " + currentDate + "\n\n" + formattedImageTitle + "\n\n" + formattedText + "\n\n" + "Credit: NASA"

### Login to Instagram ###
bot = Bot()
bot.login(username=creds.username, password=creds.password)

# Make the post
bot.upload_photo("formattedPost.jpg", caption=formattedCaption)
print("Post successful!")
