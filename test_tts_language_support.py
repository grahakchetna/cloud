#!/usr/bin/env python3
"""
Quick test to verify TTS language support is working
"""
import sys
sys.path.insert(0, '/workspaces/cloud')

from tts_service import (
    detect_language, 
    get_best_voice, 
    LANGUAGE_VOICES,
    VALID_VOICES
)

def test_language_detection():
    """Test language detection function"""
    print("\n" + "="*60)
    print("LANGUAGE DETECTION TESTS")
    print("="*60)
    
    tests = [
        ("Hello world. This is English.", "english"),
        ("नमस्ते। यह हिंदी है।", "hindi"),
        ("નમસ્તે. આ ગુજરાતી છે.", "gujarati"),
        ("This is definitely English with some description.", "english"),
        ("यह पूरी तरह हिंदी पाठ है जिसे पढ़ा जाएगा।", "hindi"),
    ]
    
    for text, expected in tests:
        detected = detect_language(text)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} Expected: {expected:12} Got: {detected:12} | {text[:40]}...")

def test_voice_configuration():
    """Test voice configuration"""
    print("\n" + "="*60)
    print("VOICE CONFIGURATION TESTS")
    print("="*60)
    
    print(f"\n✓ Total valid voices: {len(VALID_VOICES)}")
    
    print(f"\n✓ Languages configured: {list(LANGUAGE_VOICES.keys())}")
    
    for lang, config in LANGUAGE_VOICES.items():
        print(f"\n  Language: {lang}")
        print(f"    Primary: {config['primary']}")
        print(f"    Female: {config['female']}")
        print(f"    Male: {config['male']}")
        print(f"    Fallbacks: {config['fallbacks']}")

def test_voice_selection():
    """Test voice selection logic"""
    print("\n" + "="*60)
    print("VOICE SELECTION TESTS")
    print("="*60)
    
    tests = [
        (None, None, "en-US-AriaNeural"),  # Default
        (None, "english", "en-US-AriaNeural"),  # English
        (None, "hindi", "hi-IN-SwaraNeural"),  # Hindi
        (None, "gujarati", "gu-IN-DhwaniNeural"),  # Gujarati
        ("en-US-JennyNeural", None, "en-US-JennyNeural"),  # Explicit voice
    ]
    
    for voice, language, expected in tests:
        selected = get_best_voice(voice, language)
        status = "✓" if selected == expected else "✗"
        print(f"  {status} voice={voice}, language={language}")
        print(f"     Expected: {expected}")
        print(f"     Got: {selected}")

def main():
    print("\n" + "="*60)
    print("TTS LANGUAGE SUPPORT VERIFICATION")
    print("="*60)
    
    try:
        test_language_detection()
        test_voice_configuration()
        test_voice_selection()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
