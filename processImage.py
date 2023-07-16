from PIL import Image  

def cropOrResizeimage(inputImagePath, outputImagePath, targetSize):
    # Open the image
    image = Image.open(inputImagePath)
    
    # Calculate the current aspect ratio
    aspectRatio = image.width / image.height
    
    # Calculate the new dimensions
    if aspectRatio > 1:
        # Landscape image
        newWidth = int(targetSize * aspectRatio)
        newHeight = targetSize
    else:
        # Portrait or square image
        newWidth = targetSize
        newHeight = int(targetSize / aspectRatio)
    
    # Resize the image while maintaining aspect ratio
    resizedImage = image.resize((newWidth, newHeight), Image.LANCZOS)
    
    # Calculate the crop box coordinates
    left = (resizedImage.width - targetSize) // 2
    top = (resizedImage.height - targetSize) // 2
    right = left + targetSize
    bottom = top + targetSize
    
    # Crop the image to the target size
    croppedImage = resizedImage.crop((left, top, right, bottom))
    
    # Save the cropped or resized image
    croppedImage.save(outputImagePath)
