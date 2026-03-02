from PIL import Image, ImageDraw
import os
import video_service

os.makedirs('uploads', exist_ok=True)
# create test image
img = Image.new('RGB', (800,1200), color=(73,109,137))
d = ImageDraw.Draw(img)
d.text((20,20),'TEST IMAGE',(255,255,0))
img_path = 'uploads/test_image.jpg'
img.save(img_path)
print('Created test image:', img_path, 'size=', os.path.getsize(img_path))

# ensure directories
os.makedirs('videos', exist_ok=True)

# ensure short layout
video_service.WIDTH = 1080
video_service.HEIGHT = 1920

out = video_service.generate_video('Test Headline', 'Test description', 'assets/music.mp3', language='english', output_path='videos/test_short_video.mp4', media_paths=[img_path])
print('Generated video:', out)
