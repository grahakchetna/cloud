from moviepy.editor import *
from moviepy.audio.fx import all as afx
from moviepy.video.compositing.concatenate import concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap
import tempfile
import os
import json
import logging
from datetime import datetime
import subprocess
import numpy as np
import re


Image.ANTIALIAS = Image.Resampling.LANCZOS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIDTH = 1080
HEIGHT = 1920

VIDEOS_DIR = "videos"
VIDEO_MANIFEST = os.path.join(VIDEOS_DIR, "manifest.json")

# Enhanced professional colors
COLOR_ACCENT_RED = (220, 20, 60)     # Crimson red for better contrast
COLOR_ACCENT_DARK_RED = (139, 0, 0)  # Dark red
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_SHADOW = (0, 0, 0)
COLOR_OVERLAY_BG = (0, 0, 0)

# Try to find fonts on common Linux locations
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

# Gujarati and Indian script fonts
INDIC_FONT_PATHS = [
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
    "/usr/share/fonts/truetype/droid/DroidSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerifGujarati-Regular.ttf",
    "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
    "/usr/share/fonts/truetype/lohit-gujarati/Lohit-Gujarati.ttf",
    "/usr/share/fonts/truetype/mangal.ttf",
]

# Map language to font paths
LANGUAGE_FONT_MAP = {
    "gujarati": INDIC_FONT_PATHS,
    "hindi": INDIC_FONT_PATHS,
    "default": FONT_PATHS
}

def get_font(bold=False, language="default"):
    """Get available font, fallback to default if not found"""
    # Try configured paths first
    font_paths = LANGUAGE_FONT_MAP.get(language, FONT_PATHS)
    for path in font_paths:
        if os.path.exists(path):
            return path

    # If not found, try system font listing via fc-list (if available)
    try:
        fc_list = subprocess.check_output(["fc-list", "--format", "%{file}\n"]).decode(errors="ignore")
        lines = [l.strip() for l in fc_list.splitlines() if l.strip()]

        # Language-specific keywords to look for in font file paths
        keywords = []
        lang = (language or "").lower()
        if "gujarati" in lang:
            keywords = ["gujarati", "noto", "lohit", "guj", "gujr"]
        elif "hindi" in lang or "devanagari" in lang:
            keywords = ["devanagari", "noto", "mangal", "lohit", "dev"]
        else:
            keywords = ["noto", "dejavu", "liberation", "freefont"]

        for l in lines:
            low = l.lower()
            for kw in keywords:
                if kw in low:
                    if os.path.exists(l):
                        return l
    except Exception:
        # fc-list not available or failed — ignore
        pass

    return None  # Use default PIL font if no font file found


def _find_working_font_for_text(text: str, fontsize: int, candidate_paths=None):
    """Try candidate font files and return the first ImageFont that can render `text` without encoding errors."""
    if candidate_paths is None:
        candidate_paths = FONT_PATHS + INDIC_FONT_PATHS

    # include runtime scan of /usr/share/fonts for additional ttf files
    for root in ("/usr/share/fonts", "/usr/local/share/fonts", "/usr/share/fonts/truetype"):
        try:
            for dirpath, dirnames, filenames in os.walk(root):
                for fn in filenames:
                    if fn.lower().endswith((".ttf", ".otf")):
                        candidate_paths.append(os.path.join(dirpath, fn))
        except Exception:
            continue

    seen = set()
    for path in candidate_paths:
        if not path or path in seen:
            continue
        seen.add(path)
        try:
            if not os.path.exists(path):
                continue
            f = ImageFont.truetype(path, fontsize)
            # quick test: try to get bbox or mask for the text
            try:
                f.getbbox(text)
                return f
            except Exception:
                try:
                    f.getmask(text)
                    return f
                except Exception:
                    continue
        except Exception:
            continue

    return None

FONT_REGULAR = get_font(bold=False)
FONT_BOLD = get_font(bold=True)
FONT_GUJARATI = get_font(bold=False, language="gujarati")
FONT_GUJARATI_BOLD = get_font(bold=True, language="gujarati")

def add_text_shadow(draw, text, position, font, shadow_offset=3):
    """Helper to add text shadow for better readability"""
    x, y = position
    # Draw shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(*COLOR_SHADOW, 200))

def create_boxed_text_image(text, fontsize=40, color=(255, 255, 255), bold=True, box_width=600, box_height=1100, language="en"):
    """Create a text image clipped to a fixed box size (600×1100) with visible border.
    
    If text exceeds box height, the image will be taller (for scrolling).
    If text is shorter, it's positioned at the top.
    """
    if language in ["gujarati", "hindi"]:
        font_path = FONT_GUJARATI_BOLD if bold else FONT_GUJARATI
    else:
        font_path = FONT_BOLD if bold else FONT_REGULAR
    
    try:
        if font_path:
            font = ImageFont.truetype(font_path, fontsize)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Ensure font can render text
    try:
        font.getbbox(text)
    except Exception:
        found = _find_working_font_for_text(text, fontsize)
        if found:
            font = found
    
    # Wrap text to fit within box_width
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        
        if line_width > box_width - 40 and current_line:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line.strip())
    
    # Calculate actual height needed
    line_height = fontsize + 10
    img_height = max(len(lines) * line_height + 20, box_height)  # At least box_height
    img_width = box_width + 40
    shadow_offset = 3
    padding = 15
    
    # Create image with transparency
    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw semi-transparent background box for visibility
    box_coords = [(5, 5), (img_width - 5, min(box_height, img_height) - 5)]
    draw.rectangle(box_coords, fill=(0, 0, 0, 60))
    
    # Draw text with shadow
    y = padding
    for line in lines:
        draw.text((10 + shadow_offset, y + shadow_offset), line, font=font, fill=(*COLOR_SHADOW, 180))
        draw.text((10, y), line, font=font, fill=(*color, 255))
        y += line_height
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    return temp_file.name, img_height


def create_text_image(text, fontsize=65, color=(255, 255, 255), bold=False, max_width=620, language="en", add_shadow=True):
    """Create text image using PIL instead of ImageMagick with optional shadow"""
    if language in ["gujarati", "hindi"]:
        font_path = FONT_GUJARATI_BOLD if bold else FONT_GUJARATI
    else:
        font_path = FONT_BOLD if bold else FONT_REGULAR
    
    try:
        if font_path:
            font = ImageFont.truetype(font_path, fontsize)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # For Gujarati/Hindi, try to find working font if default fails
    if language in ["gujarati", "hindi"]:
        try:
            test_char = text[0] if text else "\u0aa0"  # test gujarati char
            font.getbbox(test_char)
        except Exception:
            working_font = _find_working_font_for_text(text, fontsize, INDIC_FONT_PATHS + FONT_PATHS)
            if working_font:
                font = working_font
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        try:
            bbox = font.getbbox(test_line)
            line_width = bbox[2] - bbox[0]
        except Exception:
            # fallback estimate if font can't render this text
            line_width = len(test_line) * fontsize * 0.6
        
        if line_width > max_width and current_line:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line.strip())

    
    # Calculate image size with proper spacing
    line_height = fontsize + 10
    shadow_offset = 3 if add_shadow else 0
    img_height = len(lines) * line_height + 20 + shadow_offset
    img_width = max_width + 40 + shadow_offset
    
    # Create image with transparency
    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw text with shadow
    y = 10
    for line in lines:
        try:
            if add_shadow:
                draw.text((10 + shadow_offset, y + shadow_offset), line, font=font, fill=(*COLOR_SHADOW, 180))
            draw.text((10, y), line, font=font, fill=(*color, 255))
        except Exception as e:
            logger.warning(f"Failed to draw line in create_text_image: {e}")
        y += line_height
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    return temp_file.name, img_height


def create_ticker_text_image(text, fontsize=50, color=(255, 255, 255), bold=True, language="en"):
    """Create a single-line text image for ticker scrolling with shadow"""
    if language in ["gujarati", "hindi"]:
        font_path = FONT_GUJARATI_BOLD if bold else FONT_GUJARATI
    else:
        font_path = FONT_BOLD if bold else FONT_REGULAR
    
    try:
        if font_path:
            font = ImageFont.truetype(font_path, fontsize)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Ensure the font can render the provided text; if not, try to find a working font
    try:
        font.getbbox(text)
    except Exception:
        found = _find_working_font_for_text(text, fontsize)
        if found:
            font = found
    
    # Create image with extra width for scrolling (wider for long headlines)
    img_height = fontsize + 30
    # Use the video WIDTH to size ticker appropriately; fall back to 1200
    try:
        base_width = max(1200, int(getattr(__import__("video_service"), 'WIDTH', 1080) * 1.2))
    except Exception:
        base_width = 1400
    img_width = max(base_width, len(text) * 25)
    shadow_offset = 3
    
    # Create image
    img = Image.new("RGBA", (img_width + shadow_offset, img_height + shadow_offset), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw shadow
    draw.text((20 + shadow_offset, 15 + shadow_offset), text, font=font, fill=(*COLOR_SHADOW, 180))
    # Draw text
    draw.text((20, 15), text, font=font, fill=(*color, 255))
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    return temp_file.name, img_height


def create_right_content_box(text, fontsize=32, color=(255, 255, 255), bold=True, language="en"):
    """Create a right-side content box with headline text.
    
    This is displayed on the right side when no media is available.
    Design: semi-transparent background with text centered vertically.
    Dimensions optimized for 1080x1920 (9:16) vertical format.
    
    Returns: (image_path, width, height)
    """
    if language in ["gujarati", "hindi"]:
        font_path = FONT_GUJARATI_BOLD if bold else FONT_GUJARATI
    else:
        font_path = FONT_BOLD if bold else FONT_REGULAR
    
    try:
        if font_path:
            font = ImageFont.truetype(font_path, fontsize)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # Ensure font can render text
    try:
        font.getbbox(text)
    except Exception:
        found = _find_working_font_for_text(text, fontsize)
        if found:
            font = found
    
    # Right content box dimensions (optimized for 9:16 format)
    box_width = int(WIDTH * 0.45)  # 45% of screen width
    box_height = 200  # min-height
    padding = 25
    
    # Wrap text to fit within box
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        
        if line_width > (box_width - padding - padding) and current_line:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line.strip())
    
    # Calculate actual image dimensions
    line_height = fontsize + 8
    text_height = len(lines) * line_height
    img_height = max(box_height, text_height + padding * 2)
    img_width = box_width + padding * 2
    
    # Create image with transparency
    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw semi-transparent background with blur effect (simulated with darker overlay)
    # Background: rgba(0, 0, 0, 0.45) == 45% opacity black
    shadow_offset = 3
    
    # Draw rounded corner background (approximated with rectangle)
    bg_coords = [(padding // 2, padding // 2), 
                 (img_width - padding // 2, img_height - padding // 2)]
    draw.rectangle(bg_coords, fill=(0, 0, 0, 115))  # 0.45 * 255 ≈ 115
    
    # Draw text with shadow for better readability
    y = padding
    for line in lines:
        # Shadow
        draw.text((padding + shadow_offset, y + shadow_offset), line, font=font, 
                 fill=(*COLOR_SHADOW, 180))
        # Main text
        draw.text((padding, y), line, font=font, fill=(*color, 255))
        y += line_height
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    return temp_file.name, img_width, img_height


def generate_video(title, description, audio_path, language="en", use_female_anchor=True, output_path=None, max_duration=None, media_path=None, media_paths=None,
                  layout_mediaPosition="right", layout_mediaSize="medium", layout_mediaOpacity=100, 
                  layout_textAlignment="center", layout_backgroundBlur="light", desc_to_ticker_on_media=False):
    """Generate a video from provided audio and assets.

    Args:
        title: Headline text (used for ticker and right content box if no media)
        description: Description text (used for description box on right side if media unavailable)
        audio_path: Path to narration audio file
        language: Language for text rendering ("en", "gujarati", "hindi")
        use_female_anchor: Whether to use female anchor
        output_path: Custom output path
        max_duration: Optional max duration in seconds
        media_path: Optional single path to media file (image or video) to display on right side.
                    This argument is still supported for backwards compatibility.
        media_paths: Optional list of paths which will be cycled/concatenated for the duration.
        layout_mediaPosition: Position of media ('left', 'right', 'center')
        layout_mediaSize: Size of media ('small', 'medium', 'large', 'full')
        layout_mediaOpacity: Opacity of media (0-100)
        layout_textAlignment: Text alignment ('left', 'center', 'right')
        layout_backgroundBlur: Background blur effect ('none', 'light', 'medium', 'heavy')

    Returns:
        Path to generated video file
    """
    if output_path is None:
        output_path = "static/final_video.mp4"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    voice = AudioFileClip(audio_path)
    # Trim audio if a maximum duration is requested
    if max_duration and voice.duration > float(max_duration):
        voice = voice.subclip(0, float(max_duration))

    duration = voice.duration

    # Select appropriate background image (short vs long) based on current dimensions
    if WIDTH > 1080:
        # horizontal long-video background
        bg_path = "longbg.png"
    else:
        bg_path = "shortbg.png"

    # Background
    try:
        if os.path.exists(bg_path):
            logger.info(f"Loading background: {bg_path}")
            bg_img = ImageClip(bg_path)
            bg = bg_img.resize((WIDTH, HEIGHT)).set_duration(duration)
            logger.info("✓ Background loaded")
        else:
            logger.warning(f"Background not found: {bg_path}, using bg.mp4")
            bg = (
                VideoFileClip("assets/bg.mp4")
                .resize((WIDTH, HEIGHT))
                .subclip(0, duration)
            )
    except Exception as e:
        logger.error(f"Failed to load background: {e}. Falling back to bg.mp4")
        bg = (
            VideoFileClip("assets/bg.mp4")
            .resize((WIDTH, HEIGHT))
            .subclip(0, duration)
        )

    overlay = (
        ColorClip((WIDTH, HEIGHT), color=COLOR_OVERLAY_BG)
        .set_opacity(0.15 if layout_backgroundBlur == "light" else (0.25 if layout_backgroundBlur == "medium" else (0.4 if layout_backgroundBlur == "heavy" else 0.08)))
        .set_duration(duration)
    )

    # Anchor - perfect position (left side, centered vertically)
    anchor_height = 750
    anchor_y = int((HEIGHT - anchor_height) / 2)  # Center vertically
    anchor = (
        ImageClip("static/anchor.png")
        .resize(height=anchor_height)
        .set_position((40, anchor_y))
        .set_duration(duration)
    )

    # Logo - moved to right corner
    logo = (
        ImageClip("static/logo.jpg")
        .resize(height=100)
        .set_position((WIDTH - 130, 40))
        .set_duration(duration)
    )

    # ============= TOP RED HEADLINE BAR =============
    headline_bar_height = 120
    headline_bar_y = 150
    
    # Red background bar with gradient effect (simulated with darker red border)
    headline_bar = (
        ColorClip((WIDTH, headline_bar_height), color=COLOR_ACCENT_RED)
        .set_position(("center", headline_bar_y))
        .set_duration(duration)
    )
    
    # Add dark red border effect (creates depth)
    headline_bar_border = (
        ColorClip((WIDTH, 3), color=COLOR_ACCENT_DARK_RED)
        .set_position(("center", headline_bar_y + headline_bar_height - 3))
        .set_duration(duration)
    )

    # Create scrolling ticker text using headline (same variable for ticker and right box)
    headline = title  # Use headline variable consistently
    ticker_img_path, ticker_height = create_ticker_text_image(
        headline,
        fontsize=50,
        color=(255, 255, 255),
        bold=True,
        language=language
    )
    
    # Create scrolling animation - text moves from right to left
    ticker_clip = ImageClip(ticker_img_path).set_duration(duration)
    
    # Animation function for scrolling
    def make_ticker_position(t):
        # Speed: move across screen in duration seconds, then loop
        scroll_speed = WIDTH + 4500  # Total distance to scroll - increased for faster speed
        x_pos = WIDTH - (t % duration) * (scroll_speed / duration)
        # Center ticker vertically inside the headline bar (tight)
        y_center = int(headline_bar_y + (headline_bar_height - ticker_height) / 2)
        return (x_pos, y_center)
    
    ticker_clip = ticker_clip.set_position(make_ticker_position)

    # Background behind ticker text: semi-transparent black (80% opacity)
    try:
        ticker_bg = (
            ColorClip((WIDTH, ticker_height + 20), color=(0, 0, 0))
            .set_opacity(0.8)
            .set_position(("center", int(headline_bar_y + (headline_bar_height - (ticker_height + 20)) / 2)))
            .set_duration(duration)
        )
    except Exception:
        ticker_bg = None

    # Define breaking bar Y early so right-side layout can reference it
    breaking_bar_y = HEIGHT - 220
    # vertical start for description/media box area (just below headline bar)
    desc_start_y = headline_bar_y + headline_bar_height + 10

    # ============= MEDIA POSITIONING BASED ON LAYOUT PARAMETERS =============
    # Determine media width/height based on size parameter
    size_map = {"small": 0.35, "medium": 0.5, "large": 0.7, "full": 1.0}
    media_width_percent = size_map.get(layout_mediaSize, 0.5)
    
    # Calculate media dimensions
    if layout_mediaPosition == "center" and layout_mediaSize == "full":
        right_content_width = WIDTH
        right_content_x = 0
    elif layout_mediaPosition == "center":
        right_content_width = int(WIDTH * media_width_percent)
        right_content_x = int((WIDTH - right_content_width) / 2)
    elif layout_mediaPosition == "left":
        right_content_width = int(WIDTH * media_width_percent)
        right_content_x = 0
    else:  # right (default)
        right_content_width = int(WIDTH * media_width_percent)
        right_content_x = int(WIDTH * (1 - media_width_percent))

    # ============= RIGHT SIDE CONTENT (SHORT LAYOUT: FIXED BOX) =============
    # Position on right side - for short layout we restore a fixed box positioned
    # between the headline bar and breaking bar to avoid overlap and provide
    # consistent scrolling behavior for long descriptions.

    # Determine effective media list (media_paths takes precedence)
    effective_media_list = []
    if media_paths and isinstance(media_paths, (list, tuple)) and len(media_paths) > 0:
        effective_media_list = [p for p in media_paths if p]
    elif media_path:
        effective_media_list = [media_path]

    use_text_box = True
    right_content_clip = None
    right_bg_box = None
    
    if effective_media_list:
        # build a composite media clip that spans the entire duration
        logger.info(f"Media list provided ({len(effective_media_list)} item(s)) - preparing composite clip")
        try:
            clips = []
            for i, mp in enumerate(effective_media_list):
                logger.info(f"Processing media {i+1}/{len(effective_media_list)}: {mp}")
                if not os.path.exists(mp):
                    logger.warning(f"Media path does not exist: {mp}")
                    continue
                try:
                    if mp.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        logger.info(f"  Loading as video...")
                        clip = VideoFileClip(mp)
                        clip = clip.resize((right_content_width, int(right_content_width * clip.h / clip.w)))
                        clip = clip.subclip(0, min(clip.duration, duration))
                    else:
                        logger.info(f"  Loading as image...")
                        img = ImageClip(mp)
                        aspect = img.w / img.h if img.h > 0 else 1
                        height = int(right_content_width / aspect)
                        clip = img.resize((right_content_width, height)).set_duration(duration)
                    clips.append(clip)
                    logger.info(f"  ✓ Successfully loaded media {i+1}")
                except Exception as e:
                    logger.error(f"  ✗ Failed to load media {i+1} ({mp}): {e}")
                    continue
                    
            if clips:
                logger.info(f"Successfully loaded {len(clips)} clip(s), combining...")
                if len(clips) > 1:
                    combined = concatenate_videoclips(clips, method="compose")
                else:
                    combined = clips[0]
                if combined.duration < duration:
                    combined = concatenate_videoclips([combined] * int(duration / combined.duration + 1)).subclip(0, duration)
                media_clip = combined
                media_height = media_clip.h

                # compute space available for right content
                desc_start_y = headline_bar_y + headline_bar_height + 10
                bottom_limit = breaking_bar_y - 20
                available_height = bottom_limit - desc_start_y

                # ==== short-video special case: split box into media + scrolling text ====
                if WIDTH == 1080:
                    # determine how much vertical space to give media (half by default)
                    media_part_height = min(media_height, available_height // 2)
                    if media_part_height <= 0:
                        media_part_height = media_height
                    # resize media to fit its part
                    media_clip = media_clip.resize(height=media_part_height)
                    media_height = media_clip.h
                    media_clip = media_clip.set_position((right_content_x, desc_start_y))
                    media_clip = media_clip.set_opacity(layout_mediaOpacity / 100.0)

                    # build description clip for remainder
                    desc_x = right_content_x
                    desc_width = 450  # matches old short layout width
                    desc_box_height = max(1, available_height - media_part_height)
                    # reuse existing text-box generation/scrolling logic
                    desc_img_path, desc_height = create_boxed_text_image(
                        description,
                        fontsize=40,
                        color=(255, 255, 255),
                        bold=False,
                        box_width=desc_width,
                        box_height=desc_box_height,
                        language=language
                    )
                    # scrolling
                    if desc_height > desc_box_height:
                        from PIL import Image as PILImage
                        import numpy as np

                        full_img = PILImage.open(desc_img_path)

                        def desc_make_frame(t):
                            scroll_duration = duration * 0.35
                            if t < scroll_duration:
                                scroll_distance = desc_height - desc_box_height
                                y_scroll = int((t / scroll_duration) * scroll_distance)
                            else:
                                y_scroll = int(desc_height - desc_box_height)

                            cropped = full_img.crop((0, y_scroll, desc_width, y_scroll + desc_box_height))
                            if cropped.mode == 'RGBA':
                                cropped = cropped.convert('RGB')
                            return np.array(cropped)

                        from moviepy.video.VideoClip import VideoClip
                        desc_clip = VideoClip(make_frame=desc_make_frame, duration=duration)
                        desc_clip = desc_clip.set_position((desc_x, desc_start_y + media_part_height))
                    else:
                        desc_clip = ImageClip(desc_img_path).set_duration(duration)
                        desc_clip = desc_clip.set_position((desc_x, desc_start_y + media_part_height))

                    # combine media & text into single right-side clip
                    right_content_clip = CompositeVideoClip([media_clip, desc_clip]).set_duration(duration)
                    right_bg_box = None
                    use_text_box = False
                    logger.info("✓ Short-video: combined media + scrolling description prepared")
                else:
                    # center vertically by default
                    right_content_y = int((HEIGHT - media_height) / 2)
                    # for long video (horizontal) force media into text-box vertical area
                    if WIDTH > 1080:
                        # ensure media does not overflow below the breaking bar
                        max_media_height = breaking_bar_y - desc_start_y - 10
                        if media_height > max_media_height and max_media_height > 0:
                            # resize to fit the vertical space available
                            media_clip = media_clip.resize(height=max_media_height)
                            media_height = media_clip.h
                        right_content_y = desc_start_y
                    media_clip = media_clip.set_position((right_content_x, right_content_y))
                    media_clip = media_clip.set_opacity(layout_mediaOpacity / 100.0)
                    
                    # FORCE: Always generate text box alongside media container
                    # This ensures both containers are visible regardless of media presence
                    logger.info("Generating text box container to accompany media...")
                    desc_x = right_content_x
                    # Position text box below media or next to it
                    if WIDTH == 1080:
                        # Short video: position text box below media
                        desc_start_y_text = right_content_y + media_height + 10
                        desc_width = 450
                        desc_box_height = max(1, breaking_bar_y - desc_start_y_text - 20)
                    else:
                        # Long video: position text box below media
                        desc_start_y_text = desc_start_y + media_height + 10
                        desc_width = right_content_width
                        desc_box_height = max(1, breaking_bar_y - desc_start_y_text - 20)
                    
                    # Create text box
                    desc_img_path, desc_height = create_boxed_text_image(
                        description,
                        fontsize=40,
                        color=(255, 255, 255),
                        bold=False,
                        box_width=desc_width,
                        box_height=desc_box_height,
                        language=language
                    )
                    
                    # Background box for text
                    desc_bg_box = (
                        ColorClip((desc_width, desc_box_height), color=(0, 0, 0))
                        .set_opacity(0.6 * (layout_mediaOpacity / 100.0))
                        .set_position((desc_x, desc_start_y_text))
                        .set_duration(duration)
                    )
                    
                    desc_border = (
                        ColorClip((desc_width, 3), color=(255, 215, 0))
                        .set_position((desc_x, desc_start_y_text))
                        .set_duration(duration)
                    )
                    
                    # Handle scrolling if text is too long for box
                    if desc_height > desc_box_height:
                        logger.info(f"Description scrolling enabled (height {desc_height} > box {desc_box_height})")
                        from PIL import Image as PILImage
                        import numpy as np

                        full_img = PILImage.open(desc_img_path)

                        def desc_make_frame(t):
                            scroll_duration = duration * 0.35
                            if t < scroll_duration:
                                scroll_distance = desc_height - desc_box_height
                                y_scroll = int((t / scroll_duration) * scroll_distance)
                            else:
                                y_scroll = int(desc_height - desc_box_height)

                            cropped = full_img.crop((0, y_scroll, desc_width, y_scroll + desc_box_height))
                            if cropped.mode == 'RGBA':
                                cropped = cropped.convert('RGB')
                            return np.array(cropped)

                        from moviepy.video.VideoClip import VideoClip
                        desc_clip = VideoClip(make_frame=desc_make_frame, duration=duration)
                        desc_clip = desc_clip.set_position((desc_x, desc_start_y_text))
                    else:
                        desc_clip = ImageClip(desc_img_path).set_duration(duration)
                        desc_clip = desc_clip.set_position((desc_x, desc_start_y_text))
                    
                    # Combine media and text into single right-side clip
                    right_content_clip = CompositeVideoClip([media_clip, desc_bg_box, desc_border, desc_clip]).set_duration(duration)
                    right_bg_box = None
                    use_text_box = False
                    logger.info(f"✓ Media + text container composite prepared successfully")
            else:
                logger.info(f"No clips loaded from media list, falling back to text box")
                use_text_box = True
        except Exception as e:
            logger.warning(f"Failed to prepare composite media clip: {e} - falling back to text box")
            use_text_box = True
    else:
        use_text_box = True

    # If no media, use a fixed description box positioned between the headline
    # bar and breaking bar to prevent overlap (restored from older short-layout).
    # FORCE: Always generate both media container (empty placeholder) and text container
    if use_text_box:
        logger.info("Using fixed-position description box on right side (short layout)")

        # Fixed dimensions and positions (based on previous short layout)
        desc_x = right_content_x
        desc_start_y = headline_bar_y + headline_bar_height + 10  # just below headline bar
        # Ensure we leave space above the breaking bar
        bottom_limit = breaking_bar_y - 20
        # Identify whether any media was actually loaded (we're in the
        # use_text_box branch because no media or load failed)
        no_media_loaded = not effective_media_list
        # Separate widths and heights for short (1080x1920) and long (1920x1080) videos
        if WIDTH == 1080:
            # Short video adjustments: narrower width, taller height
            # FORCED: Always reserve space for media container at top, text below
            media_container_height = 300  # Fixed height for empty media container
            desc_width = 450
            desc_box_height = max(1, breaking_bar_y - desc_start_y - media_container_height - 20)
        else:
            # Long video: horizontal 1920x1080
            media_container_height = 250  # Fixed height for empty media container
            desc_width = 850
            desc_box_height = max(1, breaking_bar_y - desc_start_y - media_container_height - 20)

        # FORCE: Generate empty media container placeholder (whether media is present or not)
        media_placeholder = (
            ColorClip((right_content_width, media_container_height), color=(20, 20, 20))
            .set_opacity(0.7)
            .set_position((right_content_x, desc_start_y))
            .set_duration(duration)
        )
        
        # Add border to media placeholder
        media_placeholder_border = (
            ColorClip((right_content_width, 2), color=(255, 215, 0))
            .set_position((right_content_x, desc_start_y + media_container_height))
            .set_duration(duration)
        )
        
        logger.info(f"Generated empty media container placeholder (size: {right_content_width}x{media_container_height})")

        # Create description text clipped to box
        desc_img_path, desc_height = create_boxed_text_image(
            description,
            fontsize=40,
            color=(255, 255, 255),
            bold=False,
            box_width=desc_width,
            box_height=desc_box_height,
            language=language
        )

        # Background box and optional border
        desc_start_y_for_text = desc_start_y + media_container_height + 2
        desc_bg_box = (
            ColorClip((desc_width, desc_box_height), color=(0, 0, 0))
            .set_opacity(0.6 * (layout_mediaOpacity / 100.0))
            .set_position((desc_x, desc_start_y_for_text))
            .set_duration(duration)
        )

        desc_border = (
            ColorClip((desc_width, 3), color=(255, 215, 0))
            .set_position((desc_x, desc_start_y_for_text))
            .set_duration(duration)
        )

        # If text is taller than the box, create scrolling animation with masking
        if desc_height > desc_box_height:
            logger.info(f"Description scrolling enabled (height {desc_height} > box {desc_box_height})")
            from PIL import Image as PILImage
            import numpy as np

            full_img = PILImage.open(desc_img_path)

            def desc_make_frame(t):
                scroll_duration = duration * 0.35
                if t < scroll_duration:
                    scroll_distance = desc_height - desc_box_height
                    y_scroll = int((t / scroll_duration) * scroll_distance)
                else:
                    y_scroll = int(desc_height - desc_box_height)

                cropped = full_img.crop((0, y_scroll, desc_width, y_scroll + desc_box_height))
                if cropped.mode == 'RGBA':
                    cropped = cropped.convert('RGB')
                return np.array(cropped)

            from moviepy.video.VideoClip import VideoClip
            desc_clip = VideoClip(make_frame=desc_make_frame, duration=duration)
            desc_clip = desc_clip.set_position((desc_x, desc_start_y_for_text))
        else:
            desc_clip = ImageClip(desc_img_path).set_duration(duration)
            desc_clip = desc_clip.set_position((desc_x, desc_start_y_for_text))

        # FORCE: Combine both media placeholder and text into composite
        right_content_clip = CompositeVideoClip([
            media_placeholder, 
            media_placeholder_border,
            desc_bg_box, 
            desc_border,
            desc_clip
        ]).set_duration(duration)
        right_bg_box = None
    
    # ============= BOTTOM BREAKING NEWS BAR =============
    # Use same headline text for ticker consistency
    breaking_bar = (
        ColorClip((WIDTH, 130), color=COLOR_ACCENT_RED)
        .set_position(("center", breaking_bar_y))
        .set_duration(duration)
    )
    
    # Add dark red border for depth
    breaking_bar_border = (
        ColorClip((WIDTH, 3), color=COLOR_ACCENT_DARK_RED)
        .set_position(("center", breaking_bar_y))
        .set_duration(duration)
    )

    # compose full breaking-news ticker text from provided multiline string
    breaking_raw = (
        "Grahak Chetna । "
        "Email: info@grahakchetna.in web : www.grahakchetna.in "
        "Editor-in-Chief: Hardik Gajjar "
        "For more videos, visit our Channel - Click here to Subscribe and stay Updated - "
        "Website : www.grahakchetna.in YouTube : https://www.youtube.com/@GrahakChetna "
        "X (Twitter)  : www.x.com/grahakchetna Facebook : www.facebook.com/grahakchetnanews "
        "Instagram : www.instagram.com/grahak.chetna"
    )
    # create ticker-style image like headline bar
    # Use slightly larger text and slower scroll for long (horizontal) videos
    if WIDTH > 1080:
        bt_fontsize = 48
    else:
        bt_fontsize = 40

    # When generating a long video we may want to show multiple short lines
    # sequentially rather than one big paragraph.  Split on Danda or newline.
    breaking_text = None
    if WIDTH > 1080:
        parts = [p.strip() for p in re.split(r"\s*।\s*|\n+", breaking_raw) if p.strip()]
        logger.info(f"Breaking news: split into {len(parts)} parts for long video")
        if len(parts) > 1:
            per = duration / len(parts)
            subs = []
            for i, part in enumerate(parts):
                try:
                    path, height = create_ticker_text_image(
                        part,
                        fontsize=bt_fontsize,
                        color=(255, 255, 255),
                        bold=False,
                        language="gujarati"
                    )
                    if not path or not os.path.exists(path):
                        logger.warning(f"Failed to create ticker image for part {i}, using fallback")
                        # Fallback: try English rendering
                        path, height = create_ticker_text_image(
                            part,
                            fontsize=bt_fontsize,
                            color=(255, 255, 255),
                            bold=False,
                            language="en"
                        )
                    clip = ImageClip(path).set_duration(per)
                    subs.append((clip, height))
                    logger.info(f"✓ Created ticker part {i}: '{part[:50]}...'")
                except Exception as e:
                    logger.error(f"Error creating ticker part {i}: {e} - skipping this part")
                    continue

            if subs:
                def make_pos_factory(h):
                    def pos(t):
                        scroll_speed = WIDTH + 2000
                        x_pos = WIDTH - (t % per) * (scroll_speed / per)
                        y_center = int(breaking_bar_y + (130 - h) / 2)
                        y_center = max(0, y_center - 12)
                        return (x_pos, y_center)
                    return pos

                moving_clips = []
                for clip, h in subs:
                    moving_clips.append(clip.set_position(make_pos_factory(h)))
                try:
                    breaking_text = concatenate_videoclips(moving_clips)
                    logger.info(f"✓ Breaking news ticker: concatenated {len(subs)} clips (long video, multi-part)")
                except Exception as e:
                    logger.warning(f"Failed to concatenate ticker clips: {e} - falling back to single text")
                    breaking_text = None
            else:
                logger.warning("No valid ticker parts created, will use fallback")
                breaking_text = None
        
        # Fallback for when no multi-part or parts creation failed
        if breaking_text is None:
            logger.info("Using fallback single-line ticker for long video")
            try:
                breaking_text_img_path, breaking_text_height = create_ticker_text_image(
                    breaking_raw,
                    fontsize=bt_fontsize,
                    color=(255, 255, 255),
                    bold=False,
                    language="gujarati"
                )
                if not os.path.exists(breaking_text_img_path):
                    logger.warning("Gujarati ticker image failed, trying English fallback")
                    breaking_text_img_path, breaking_text_height = create_ticker_text_image(
                        breaking_raw,
                        fontsize=bt_fontsize,
                        color=(255, 255, 255),
                        bold=False,
                        language="en"
                    )
                breaking_text_img = ImageClip(breaking_text_img_path).set_duration(duration)
                def breaking_ticker_position(t):
                    scroll_speed = WIDTH + 2000
                    x_pos = WIDTH - (t % duration) * (scroll_speed / duration)
                    y_center = int(breaking_bar_y + (130 - breaking_text_height) / 2)
                    y_center = max(0, y_center - 12)
                    return (x_pos, y_center)
                breaking_text = breaking_text_img.set_position(breaking_ticker_position)
                logger.info("✓ Breaking news ticker: single-line fallback (long video)")
            except Exception as e:
                logger.error(f"Failed to create breaking news ticker: {e} - using blank placeholder")
                breaking_text = None
    else:
        # Short video (1080x1920): always use single-line ticker
        try:
            breaking_text_img_path, breaking_text_height = create_ticker_text_image(
                breaking_raw,
                fontsize=bt_fontsize,
                color=(255, 255, 255),
                bold=False,
                language="gujarati"
            )
            if not os.path.exists(breaking_text_img_path):
                logger.warning("Gujarati ticker image failed, trying English fallback")
                breaking_text_img_path, breaking_text_height = create_ticker_text_image(
                    breaking_raw,
                    fontsize=bt_fontsize,
                    color=(255, 255, 255),
                    bold=False,
                    language="en"
                )
            breaking_text_img = ImageClip(breaking_text_img_path).set_duration(duration)
            def breaking_ticker_position(t):
                scroll_speed = WIDTH + 4500
                x_pos = WIDTH - (t % duration) * (scroll_speed / duration)
                y_center = int(breaking_bar_y + (130 - breaking_text_height) / 2)
                return (x_pos, y_center)
            breaking_text = breaking_text_img.set_position(breaking_ticker_position)
            logger.info("✓ Breaking news ticker: single-line (short video)")
        except Exception as e:
            logger.error(f"Failed to create breaking news ticker: {e} - using blank placeholder")
            breaking_text = None
    
    # Ensure breaking_text is not None - create a fallback if all else fails
    if breaking_text is None:
        logger.warning("Creating blank breaking news ticker as final fallback")
        # Create a simple text fallback if everything else failed
        try:
            from PIL import Image as PILImage
            from PIL import ImageDraw as PILImageDraw
            from PIL import ImageFont
            fallback_img = PILImage.new("RGBA", (400, 100), (0, 0, 0, 0))
            fallback_draw = PILImageDraw.Draw(fallback_img)
            fallback_draw.text((10, 10), "News Ticker", fill=(255, 255, 255, 255))
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            fallback_img.save(temp_file.name)
            temp_file.close()
            breaking_text = ImageClip(temp_file.name).set_duration(duration)
            breaking_text = breaking_text.set_position(("center", breaking_bar_y))
            logger.info("✓ Created minimal fallback ticker")
        except Exception as e:
            logger.error(f"Even fallback ticker creation failed: {e}")
            breaking_text = None

    # If media is present (we're not using the text box) and the caller
    # requested that description be placed in the breaking ticker, create
    # a ticker clip for the description instead of the right-side box.
    breaking_desc_text = None
    try:
        if (not use_text_box) and desc_to_ticker_on_media and description:
            bdt_img_path, bdt_height = create_ticker_text_image(
                description,
                fontsize=40,
                color=(255, 255, 255),
                bold=False,
                language=language
            )
            bdt_img = ImageClip(bdt_img_path).set_duration(duration)
            breaking_desc_text = bdt_img.set_position(breaking_ticker_position)
    except Exception:
        breaking_desc_text = None

    # AI label
    ai_label_img_path, _ = create_text_image(
        "AI Generated Anchor",
        fontsize=28,
        color=(255, 255, 255),
        bold=False,
        max_width=WIDTH - 100
    )
    ai_label = ImageClip(ai_label_img_path)
    ai_label = (
        ai_label
        .set_position((20, HEIGHT - 60))
        .set_duration(duration)
    )

    # Background music (loop safe)
    try:
        music_clip = AudioFileClip("assets/music.mp3")
        
        # Validate the music file has actual content
        if music_clip.duration <= 0:
            raise ValueError("Music file has no duration")
        
        if music_clip.duration < duration:
            music = afx.audio_loop(music_clip, duration=duration)
        else:
            music = music_clip.subclip(0, duration)
        
        music = music.volumex(0.08)
        
    except Exception as e:
        # If music file is missing or corrupted, use voice only
        logger.warning(f"Could not load background music: {e}")
        logger.info("Continuing with voice audio only")
        music = None

    # Create final audio (voice with optional background music)
    if music is not None:
        final_audio = CompositeAudioClip([music, voice])
    else:
        final_audio = voice

    # Build clip list and filter out any None values to avoid moviepy errors
    clips = [
        bg,
        overlay,
        anchor,
        logo,
        headline_bar,
        headline_bar_border,
        # Ticker background (if created) followed by ticker text
        ticker_bg if 'ticker_bg' in locals() and ticker_bg is not None else None,
        ticker_clip,
        # Right side content - either media or text box
        right_bg_box if 'right_bg_box' in locals() and right_bg_box is not None else None,
            right_content_clip if right_content_clip is not None else None,
        breaking_bar,
        breaking_bar_border,
        breaking_text,
        breaking_desc_text if 'breaking_desc_text' in locals() else None,
        ai_label,
    ]

    clips = [c for c in clips if c is not None]
    main_video = CompositeVideoClip(clips).set_audio(final_audio)

    # Ending screen (3 sec)
    ending_duration = 3

    ending_bg = (
        ColorClip((WIDTH, HEIGHT), color=(0, 0, 0))
        .set_duration(ending_duration)
    )

    ending_text_img_path, _ = create_text_image(
        "Presented by\nGrahak Chetna",
        fontsize=75,
        color=(255, 255, 255),
        bold=True,
        max_width=WIDTH - 100
    )
    ending_text = ImageClip(ending_text_img_path)
    ending_text = (
        ending_text
        .set_position("center")
        .set_duration(ending_duration)
    )

    ending_clip = CompositeVideoClip(
        [ending_bg, ending_text]
    ).set_duration(ending_duration)

    final = concatenate_videoclips([main_video, ending_clip])

    # Use the provided output_path or default to static/final_video.mp4
    if not output_path:
        output_path = "static/final_video.mp4"

    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
    )

    return output_path
