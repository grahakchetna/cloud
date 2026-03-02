import os
from moviepy.editor import VideoFileClip

VIDEOS_DIR = 'videos'
OUT_DIR = 'output/frames'

os.makedirs(OUT_DIR, exist_ok=True)

# find latest mp4 in videos/
mp4s = []
if os.path.exists(VIDEOS_DIR):
    for fn in os.listdir(VIDEOS_DIR):
        if fn.lower().endswith('.mp4'):
            mp4s.append(os.path.join(VIDEOS_DIR, fn))

if not mp4s:
    print('No mp4 files found in videos/ directory')
    raise SystemExit(1)

latest = max(mp4s, key=lambda p: os.path.getmtime(p))
print('Latest video:', latest)

# load video
clip = VideoFileClip(latest)
dur = clip.duration
print(f'Duration: {dur:.2f}s')

# choose timestamps
times = [min(0.5, dur/10), dur/2, max(dur-0.5, dur*0.9 if dur>1 else dur)]
# de-duplicate and clamp
times = sorted(set([max(0, min(dur, t)) for t in times]))

saved = []
for i,t in enumerate(times, start=1):
    out_path = os.path.join(OUT_DIR, f"frame_{i}_{int(t*1000)}ms.png")
    try:
        clip.save_frame(out_path, t)
        saved.append(out_path)
        print(f'Saved frame at {t:.2f}s -> {out_path}')
    except Exception as e:
        print(f'Failed to save frame at {t:.2f}s: {e}')

clip.reader.close()
clip.audio and clip.audio.reader.close()

if saved:
    print('\nFrames saved:')
    for p in saved:
        try:
            size = os.path.getsize(p)
        except Exception:
            size = 'unknown'
        print(f'- {p} ({size} bytes)')
else:
    print('No frames saved')
