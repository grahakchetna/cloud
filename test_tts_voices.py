#!/usr/bin/env python3
"""
Test script to check available Edge TTS voices and test pronunciation
"""
import asyncio
import edge_tts
import os
from pathlib import Path

async def get_available_voices():
    """Get all available voices from Edge TTS"""
    voices = await edge_tts.list_voices()
    return voices

async def test_language_voices(language_code, test_text, output_file):
    """Test a specific language voice"""
    print(f"\n{'='*60}")
    print(f"Testing: {language_code}")
    print(f"{'='*60}")
    
    voices = await get_available_voices()
    lang_voices = [v for v in voices if v['Locale'].startswith(language_code)]
    
    print(f"Found {len(lang_voices)} voices for {language_code}:")
    
    if not lang_voices:
        print(f"  No voices found for {language_code}")
        return
    
    for voice in lang_voices:
        print(f"\n  Voice: {voice['ShortName']}")
        print(f"    Full Name: {voice['FriendlyName']}")
        print(f"    Locale: {voice['Locale']}")
        print(f"    Gender: {voice['Gender']}")
    
    # Test with first available voice
    if lang_voices:
        voice = lang_voices[0]['ShortName']
        print(f"\n  Testing with: {voice}")
        try:
            communicate = edge_tts.Communicate(text=test_text, voice=voice, rate="-9%")
            await communicate.save(output_file)
            size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
            print(f"  ✓ Generated: {output_file} ({size} bytes)")
        except Exception as e:
            print(f"  ✗ Error: {e}")

async def main():
    print("\n" + "="*60)
    print("EDGE TTS VOICE TESTING")
    print("="*60)
    
    # Create output directory
    Path("tts_tests").mkdir(exist_ok=True)
    
    # Test English
    await test_language_voices(
        "en-US",
        "Hello world. This is a test of English pronunciation.",
        "tts_tests/english_test.mp3"
    )
    
    # Test Hindi
    await test_language_voices(
        "hi-IN",
        "नमस्ते। यह हिंदी भाषा की एक परीक्षा है।",
        "tts_tests/hindi_test.mp3"
    )
    
    # Test Gujarati
    await test_language_voices(
        "gu-IN",
        "નમસ્તે। આ ગુજરાતી ભાષાનું પરીક્ષણ છે।",
        "tts_tests/gujarati_test.mp3"
    )
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
