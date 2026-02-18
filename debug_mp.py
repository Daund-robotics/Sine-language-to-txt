import mediapipe
print(f"MediaPipe Version: {mediapipe.__version__}")
try:
    import mediapipe.python.solutions
    print("Imported mediapipe.python.solutions successfully")
except ImportError as e:
    print(f"Failed to import mediapipe.python.solutions: {e}")

try:
    print(f"mediapipe has solutions: {hasattr(mediapipe, 'solutions')}")
    if hasattr(mediapipe, 'solutions'):
        print(dir(mediapipe.solutions))
except Exception as e:
    print(f"Error checking solutions: {e}")

print(f"Dir of mediapipe: {dir(mediapipe)}")
