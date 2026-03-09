import pygame
import os
import time
import threading
import traceback
import speech_recognition as sr
from gtts import gTTS

# تهيئة pygame للصوت
pygame.mixer.init()

def speak(text):
    """النطق الصوتي للرد - مضمون 100% على Windows"""
    print(f"🔊 Speaking: {text}")
    try:
        # إنشاء ملف صوتي من النص
        tts = gTTS(text=text, lang='en', slow=False)
        filename = "temp_audio.mp3"
        tts.save(filename)
        
        # تشغيل الصوت باستخدام pygame
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        # انتظار حتى ينتهي الصوت
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # حذف الملف المؤقت
        pygame.mixer.music.unload()
        time.sleep(0.2)
        
        if os.path.exists(filename):
            os.remove(filename)
        
        print("✅ Speech completed\n")
        
    except Exception as e:
        print(f"❌ Error in speak(): {e}")
        print(f"📋 Error type: {type(e).__name__}")
        print("💡 Make sure you have installed: pip install gtts pygame")
        print("💡 Also check your internet connection (gTTS requires internet)\n")

# اكتشاف نية المستخدم - نسخة محسنة
def detect_intent(text):
    text = text.lower().strip()
    
    # Emergency
    if any(word in text for word in ["emergency", "help", "sos", "urgent"]):
        return "SOS", "Emergency activated. Help is on the way."
    
    # Open car
    elif any(word in text for word in ["open", "unlock"]) and ("car" in text or "door" in text):
        return "OPEN_CAR", "Car opened successfully."
    
    # Close car
    elif any(word in text for word in ["close", "shut"]) and ("car" in text or "door" in text):
        return "CLOSE_CAR", "Car closed successfully."
    
    # Lock
    elif "lock" in text and "unlock" not in text:
        return "LOCK_CAR", "Car locked successfully."
    
    # Unlock (مستقل)
    elif "unlock" in text and "car" not in text:
        return "UNLOCK_CAR", "Car unlocked successfully."
    
    # Start engine
    elif any(word in text for word in ["start", "turn on", "ignition"]) and ("car" in text or "engine" in text):
        return "START_ENGINE", "Engine started successfully."
    
    # Stop engine
    elif any(word in text for word in ["stop", "turn off", "shutdown"]) and ("car" in text or "engine" in text):
        return "STOP_ENGINE", "Engine stopped successfully."
    
    # Car status
    elif any(word in text for word in ["status", "health", "condition", "check"]):
        return "CAR_STATUS", "Your car is in good condition. All systems are normal."
    
    # Location
    elif any(word in text for word in ["where", "location", "find"]) and "car" in text:
        return "CAR_LOCATION", "Your car is parked at the last known location."
    
    # Thanks
    elif any(word in text for word in ["thank", "thanks"]):
        return "THANKS", "You're welcome! Happy to help."
    
    # Exit
    elif any(word in text for word in ["bye", "exit", "quit", "goodbye", "stop"]):
        return "EXIT", "Goodbye! Drive safely."
    
    else:
        return "UNKNOWN", f"I heard: {text}. But I'm not sure what you want. Try: open car, close car, lock, status, or help."

# الاستماع من الميكروفون - نسخة محسنة جداً
def listen():
    try:
        r = sr.Recognizer()
        
        # إعدادات محسنة للتعرف على الصوت
        r.energy_threshold = 300  # تقليل الحساسية للضوضاء
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8  # وقت أقل للانتظار بعد التوقف
        
        with sr.Microphone() as source:
            print("🎤 Listening... (Speak now)")
            print("💡 Tip: Speak clearly and wait for the beep\n")
            
            # تحسين جودة الاستماع
            print("🔧 Calibrating for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("✅ Ready!\n")
            
            try:
                # استماع مع وقت أطول وبدون timeout
                audio = r.listen(source, timeout=10, phrase_time_limit=10)
                
                print("🔄 Processing your speech...")
                
                # محاولة التعرف على الكلام
                try:
                    text = r.recognize_google(audio, language='en-US')
                    print(f"✅ You said: \"{text}\"")
                    return text
                except sr.UnknownValueError:
                    print("❌ Could not understand audio clearly")
                    print("💡 Try speaking louder or closer to the microphone\n")
                    return ""
                    
            except sr.WaitTimeoutError:
                print("⏱️ No speech detected in 10 seconds")
                print("💡 Say something or press Ctrl+C to exit\n")
                return ""
            except sr.RequestError as e:
                print(f"❌ Could not request results from Google: {e}")
                print("💡 Check your internet connection\n")
                return ""
            except Exception as e:
                print(f"❌ Unexpected error: {e}\n")
                return ""
    except sr.MicrophoneError as e:
        print(f"❌ Microphone error: {e}")
        print("💡 Check if microphone is connected and not being used by another application\n")
        return ""
    except Exception as e:
        print(f"❌ Fatal error in listen(): {e}")
        print(f"📋 Error type: {type(e).__name__}\n")
        return ""

# البرنامج الرئيسي
def main():
    print("\n" + "=" * 70)
    print("🚗 VOICE ASSISTANT FOR CAR CONTROL - ENHANCED VERSION")
    print("=" * 70)
    print("\n📌 Available Commands:")
    print("   🔓 Open/Unlock: 'open the car', 'unlock the door'")
    print("   🔒 Close/Lock: 'close the car', 'lock the door'")
    print("   🔑 Lock: 'lock'")
    print("   🚀 Start: 'start the car', 'turn on engine'")
    print("   🛑 Stop: 'stop the car', 'turn off engine'")
    print("   📊 Status: 'status', 'check car', 'health'")
    print("   📍 Location: 'where is my car', 'find my car'")
    print("   🆘 Emergency: 'emergency', 'help', 'SOS'")
    print("   👋 Exit: 'bye', 'exit', 'quit'")
    print("=" * 70)
    print("\n⚙️ Initializing voice assistant...")
    
    speak("Hello! I am your enhanced voice assistant. I am ready to help you control your car. What would you like me to do?")
    
    failed_attempts = 0
    max_failed_attempts = 3
    
    while True:
        try:
            text = listen()
            
            if text:
                # إعادة تعيين العداد عند النجاح
                failed_attempts = 0
                
                intent, response = detect_intent(text)
                print(f"\n🎯 Intent Detected: {intent}")
                print(f"💬 Response: {response}")
                print("-" * 70)
                
                speak(response)
                
                # إنهاء البرنامج
                if intent == "EXIT":
                    break
                    
            else:
                failed_attempts += 1
                if failed_attempts >= max_failed_attempts:
                    print(f"\n⚠️ No input detected {max_failed_attempts} times.")
                    speak("I haven't heard anything for a while. Say something or say bye to exit.")
                    failed_attempts = 0
                    
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted by user")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in main loop: {e}")
            print(f"📋 Error type: {type(e).__name__}")
            print(f"🔍 Full traceback:")
            traceback.print_exc()
            print("\n💡 The program will continue. If this error persists, check:")
            print("   - Internet connection (for speech recognition & gTTS)")
            print("   - Microphone permissions and availability")
            print("   - All required libraries are installed")
            print("-" * 70)
            continue

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔧 SYSTEM CHECK")
    print("=" * 70)
    print("✅ Make sure you have:")
    print("   1. ✓ Internet connection (for speech recognition & gTTS)")
    print("   2. ✓ Microphone connected and working")
    print("   3. ✓ Speakers/headphones volume at good level")
    print("   4. ✓ Quiet environment (less background noise)")
    print("\n📦 Required libraries:")
    print("   pip install gtts pygame SpeechRecognition pyaudio")
    print("=" * 70)
    
    input("\n▶️ Press ENTER to start the voice assistant...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
    finally:
        pygame.quit()
        print("\n" + "=" * 70)
        print("🔚 Voice Assistant Terminated - Goodbye!")
        print("=" * 70)