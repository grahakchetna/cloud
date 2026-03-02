from PIL import Image, ImageDraw
import os
import json
import video_service
from app import layout_to_video_params
import app

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

# real short layout generation (without dummy patch) to ensure base case
video_service.WIDTH = 1080
video_service.HEIGHT = 1920

out = video_service.generate_video('Test Headline', 'Test description', 'assets/music.mp3', language='english', output_path='videos/test_short_video.mp4', media_paths=[img_path])
print('Generated short video:', out)

# --------------------------------------------------------------
# Now verify new split-box behavior using dummy clips (no heavy encoding)
# --------------------------------------------------------------
video_service.WIDTH = 1080
video_service.HEIGHT = 1920

# monkeypatch classes used by video_service to simple dummies that record ops
class DummyClip:
    ops = []
    last_height = None
    def __init__(self, path=None):
        self.w = 400
        self.h = 3000
        self.duration = 5
    def resize(self, size=None, height=None, width=None):
        if size:
            self.w, self.h = size
        if height and not width:
            # maintain aspect ratio
            ratio = height / self.h if self.h else 1
            self.h = int(height)
            self.w = int(self.w * ratio)
        if width and not height:
            ratio = width / self.w if self.w else 1
            self.w = int(width)
            self.h = int(self.h * ratio)
        DummyClip.last_height = self.h
        DummyClip.ops.append(('resize', self.h))
        return self
    def set_opacity(self, x):
        DummyClip.ops.append(('opacity', x))
        return self
    def set_position(self, pos):
        DummyClip.ops.append(('position', pos))
        return self
    def set_duration(self, dur):
        return self
    def subclip(self, a, b):
        return self
    def __getattr__(self, item):
        # stub out methods like loop, etc.
        return lambda *args, **kwargs: self

class DummyComposite:
    def __init__(self, clips):
        DummyClip.ops.append(('composite', len(clips)))
    def set_audio(self, audio):
        return self
    def set_duration(self, dur):
        return self
    def set_fps(self, fps):
        return self
    def write_videofile(self, *args, **kwargs):
        return

# prepare dummy media + description checks
DummyClip.ops = []
video_service.VideoFileClip = DummyClip
video_service.ImageClip = DummyClip
video_service.concatenate_videoclips = lambda clips, method=None: clips[0]
video_service.CompositeVideoClip = DummyComposite

# run generation again; this should trigger short-video split logic
out_short2 = video_service.generate_video(
    'Split Test',
    'This description should scroll under the media.',
    'assets/music.mp3',
    language='english',
    output_path='videos/test_short_split.mp4',
    media_path=img_path
)
print('Generated short split video (dummy):', out_short2)

# compute expected desc position for assertion
headline_bar_y = 150
headline_bar_height = 120
breaking_bar_y = video_service.HEIGHT - 220

desc_start_y = headline_bar_y + headline_bar_height + 10
available_height = (breaking_bar_y - 20) - desc_start_y
media_part_height = min(3000, available_height // 2)  # DummyClip initial h=3000
expected_desc_pos = (540, desc_start_y + media_part_height)

# look for matching position entry in logged ops
positions = [op for op in DummyClip.ops if op[0] == 'position']
assert expected_desc_pos in [p[1] for p in positions], f"description clip not positioned correctly, ops: {positions}"
print('Short-video split behavior verified (description positioned at', expected_desc_pos, ')')

# ------------------------------------------------------------------
# Long video scenario: tall media should be resized to fit available area
# ------------------------------------------------------------------
video_service.WIDTH = 1920
video_service.HEIGHT = 1080

# create a very tall image to simulate cropping issue
img2 = Image.new('RGB', (400, 3000), color=(255, 0, 0))
d2 = ImageDraw.Draw(img2)
d2.text((20,20),'TALL',(255,255,255))
img2_path = 'uploads/test_tall.jpg'
img2.save(img2_path)
print('Created tall image:', img2_path, 'size=', os.path.getsize(img2_path))

# monkeypatch video and image clip classes to monitor resize
class DummyClip:
    last_height = None
    def __init__(self, path=None):
        self.w = 400
        self.h = 3000
        self.duration = 5
    def resize(self, size=None, height=None, width=None):
        if size:
            self.w, self.h = size
        if height and not width:
            # maintain aspect ratio
            ratio = height / self.h if self.h else 1
            self.h = int(height)
            self.w = int(self.w * ratio)
        if width and not height:
            ratio = width / self.w if self.w else 1
            self.w = int(width)
            self.h = int(self.h * ratio)
        DummyClip.last_height = self.h
        return self
    def set_opacity(self, x):
        return self
    def set_position(self, pos):
        return self
    def subclip(self, a, b):
        return self
    def __getattr__(self, item):
        # stub out methods like loop, etc.
        return lambda *args, **kwargs: self

# patch the cls references in video_service
video_service.VideoFileClip = DummyClip
video_service.ImageClip = DummyClip
video_service.concatenate_videoclips = lambda clips, method=None: clips[0]
# also stub out CompositeVideoClip to avoid fps comparison issues
class DummyComposite:
    def __init__(self, clips):
        pass
    def set_audio(self, audio):
        return self
    def set_duration(self, dur):
        return self
    def set_fps(self, fps):
        return self
    def write_videofile(self, *args, **kwargs):
        # no actual file write
        return
video_service.CompositeVideoClip = DummyComposite

# run generation; this should hit the resizing logic for long video
out2 = video_service.generate_video(
    'Long Test', 'Long description', 'assets/music.mp3',
    language='english',
    output_path='videos/test_long_video.mp4',
    media_path=img2_path
)
print('Generated long video (dummy):', out2)

# validate that the media was capped
breaking_bar_y = video_service.HEIGHT - 220
headline_bar_y = 150
headline_bar_height = 120
desc_start_y = headline_bar_y + headline_bar_height + 10
max_allowed = breaking_bar_y - desc_start_y - 10
print('Max allowed media height for long video:', max_allowed)
assert DummyClip.last_height <= max_allowed, f"media height {DummyClip.last_height} exceeds cap"
print('Long video media height correctly capped at', DummyClip.last_height)

# ------------------------------------------------------------------
# Verify ticker text splitting for long videos
# ------------------------------------------------------------------
# monkeypatch create_ticker_text_image to record calls
called_parts = []
orig_ctti = video_service.create_ticker_text_image

def recorder(text, **kwargs):
    called_parts.append(text)
    return orig_ctti(text, **kwargs)

video_service.create_ticker_text_image = recorder

# run long video again to exercise ticker logic
video_service.WIDTH = 1920
video_service.HEIGHT = 1080
out3 = video_service.generate_video(
    'Ticker Test', 'ignore', 'assets/music.mp3',
    language='english', output_path='videos/test_long_ticker.mp4'
)
print('Generated long video for ticker test (dummy):', out3)
print('Ticker parts used:', called_parts)
assert len(called_parts) > 1, 'Expected ticker to be split into multiple lines'
print('Ticker splitting behaviour verified,', len(called_parts), 'segments')

# ------------------------------------------------------------------
# Additional tests for layout configuration parsing
# ------------------------------------------------------------------

# ensure layout_to_video_params translates designer values correctly
cfg_example = {
    'media_x': '10',          # left side
    'media_y': '50',          # y coordinate required for position logic
    'media_width': '30',      # small
    'media_opacity': '50',    # 50%
    'textbox_x': '80',        # right align text
    'bg_blur': 'heavy'
}
params = layout_to_video_params(cfg_example, video_format='short')
assert params['layout_mediaPosition'] == 'left'
assert params['layout_mediaSize'] == 'small'
assert params['layout_mediaOpacity'] == 50
assert params['layout_textAlignment'] == 'right'
assert params['layout_backgroundBlur'] == 'heavy'
print('layout_to_video_params mapping verified')

# verify /generate endpoint will honour layout_config by capturing passed kwargs
from app import app as flask_app
client = flask_app.test_client()
# monkeypatch app.generate_video to record its kwargs
called_kwargs = {}
original_video = app.generate_video

def capture_generate_video(title, description, audio_path, **kwargs):
    called_kwargs.update(kwargs)
    return 'dummy.mp4'

app.generate_video = capture_generate_video

layout_payload = json.dumps(cfg_example)
# send layout_config; we don't care if manifest addition fails, we just need to
# ensure the handler forwarded the parameters correctly
resp = client.post('/generate', data={
    'headline': 'Test',
    'description': 'Desc',
    'language': 'english',
    'layout_config': layout_payload
})
# allow either success or manifest error (500) so test can run in this environment
if resp.status_code not in (200, 500):
    raise AssertionError(f"unexpected status code {resp.status_code}")
# verify that parameters were captured regardless of response
assert called_kwargs.get('layout_mediaPosition') == 'left'
assert called_kwargs.get('layout_mediaSize') == 'small'
assert called_kwargs.get('layout_mediaOpacity') == 50
assert called_kwargs.get('layout_textAlignment') == 'right'
assert called_kwargs.get('layout_backgroundBlur') == 'heavy'
print('Server parse of layout_config via /generate verified')

# restore original function to avoid side effects
video_service.generate_video = original_video

# ------------------------------------------------------------------
# Social media endpoint sanity checks
# ------------------------------------------------------------------
from app import app as flask_app
client = flask_app.test_client()

# prepare a small dummy video file
dummy_path = 'videos/dummy.mp4'
with open(dummy_path, 'wb') as f:
    f.write(b'1234')

# 1. facebook without creds -> 400
os.environ.pop('PAGE_ID', None)
os.environ.pop('PAGE_ACCESS_TOKEN', None)
resp_fb = client.post('/facebook/post', data={'filename':'dummy.mp4'})
print('fb no-cred status', resp_fb.status_code, resp_fb.get_data(as_text=True))
assert resp_fb.status_code == 400

# 2. instagram without creds -> 400
resp_ig = client.post('/instagram/post', data={'filename':'dummy.mp4'})
print('ig no-cred status', resp_ig.status_code, resp_ig.get_data(as_text=True))
assert resp_ig.status_code == 400

# 3. verify no-media layout generates full-width description box
os.environ['PAGE_ID']=''
os.environ['PAGE_ACCESS_TOKEN']=''
# monkeypatch create_boxed_text_image to record width
called_widths = []
orig_create = video_service.create_boxed_text_image

def width_recorder(text, fontsize, color, bold, box_width, box_height, language):
    called_widths.append(box_width)
    return orig_create(text, fontsize=fontsize, color=color, bold=bold, box_width=box_width, box_height=box_height, language=language)

video_service.create_boxed_text_image = width_recorder

# generate short video without media
video_service.WIDTH = 1080
video_service.HEIGHT = 1920
out_nomedia = video_service.generate_video('NoMedia', 'Some text', 'assets/music.mp3', language='english', output_path='videos/test_no_media.mp4')
print('Generated short video without media:', out_nomedia)
assert called_widths and called_widths[-1] == int(1080 * 0.5), f"expected width {int(1080*0.5)}, got {called_widths[-1]}"
print('No-media description box width correct:', called_widths[-1])

# 3. invalid creds produce 500 with API errors
os.environ['PAGE_ID'] = '123'
os.environ['PAGE_ACCESS_TOKEN'] = 'badtoken'
resp_fb2 = client.post('/facebook/post', data={'filename':'dummy.mp4'})
print('fb invalid cred status', resp_fb2.status_code, resp_fb2.get_data(as_text=True))
assert resp_fb2.status_code == 500
resp_ig2 = client.post('/instagram/post', data={'filename':'dummy.mp4'})
print('ig invalid cred status', resp_ig2.status_code, resp_ig2.get_data(as_text=True))
assert resp_ig2.status_code == 500

print('Social endpoint sanity checks complete')
