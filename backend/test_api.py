import requests
import time

API_URL = "http://127.0.0.1:8000/predict"

def test_api():
    print(f"Sending mock data to {API_URL}...")
    
    # Send all 9 features precisely + model_id
    data = {
        "model_id": "exp4-encoder-free-unified",
        "age": 45.0,
        "gender": "male",
        "tbContactHistory": True,
        "wheezingHistory": False,
        "phlegmCough": True,
        "familyAsthmaHistory": False,
        "feverHistory": True,
        "coldPresent": False,
        "packYears": 10.5
    }
    
    # Create a 1-second dummy WAV file for testing
    import wave
    import struct
    import math

    with wave.open("dummy_audio.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        # 1600 frames = 0.1 seconds (smaller test dummy)
        for i in range(1600):
            value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / 16000.0))
            data_str = struct.pack("<h", value)
            w.writeframesraw(data_str)
            
    # Send the test request
    with open("dummy_audio.wav", "rb") as f:
        files = {"audio": ("dummy_audio.wav", f, "audio/wav")}
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.post(API_URL, data=data, files=files)
                print(f"Status Code: {response.status_code}")
                print(f"Response JSON:\n{response.json()}")
                break
            except requests.exceptions.ConnectionError:
                print(f"Server not ready yet, retrying in 5 seconds... ({i+1}/{max_retries})")
                time.sleep(5)

if __name__ == "__main__":
    test_api()
