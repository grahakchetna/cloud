import io
from app import app

# create a small in-memory image
from PIL import Image
img = Image.new('RGB', (800,1200), color=(123,50,200))
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

data = {
    'headline': 'UI Test Headline',
    'description': 'UI Test Description',
    'language': 'english',
    'voice_provider': 'auto',
    'voice_model': 'auto',
    'video_length': 'short',
    'media_file_0': (buf, 'test_ui_image.jpg')
}

with app.test_client() as client:
    resp = client.post('/generate', data=data, content_type='multipart/form-data')
    print('Status code:', resp.status_code)
    try:
        print('Response JSON:', resp.get_json())
    except Exception:
        print('Response data:', resp.data[:1000])

import os
print('Uploads dir listing:', os.listdir('uploads') if os.path.exists('uploads') else 'no uploads dir')
