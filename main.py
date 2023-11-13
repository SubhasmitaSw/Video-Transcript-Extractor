import os
import speech_recognition as sr
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

num_seconds_video = 52 * 60
print("The video is {} seconds".format(num_seconds_video))

# Ensure directories exist
if not os.path.exists("chunks"):
    os.makedirs("chunks")
if not os.path.exists("converted"):
    os.makedirs("converted")

l = list(range(0, num_seconds_video + 1, 60))
diz = {}

for i in range(len(l) - 1):
    try:
        ffmpeg_extract_subclip("video.mp4", l[i] - 2 * (l[i] != 0), l[i + 1], targetname="chunks/cut{}.mp4".format(i + 1))
        clip = mp.VideoFileClip(r"chunks/cut{}.mp4".format(i + 1))
        clip.audio.write_audiofile(r"converted/converted{}.wav".format(i + 1))

        r = sr.Recognizer()
        audio = sr.AudioFile("converted/converted{}.wav".format(i + 1))

        with audio as source:
            r.adjust_for_ambient_noise(source)
            audio_file = r.record(source)

        result = r.recognize_google(audio_file)
        diz['chunk{}'.format(i + 1)] = result

    except BrokenPipeError as e:
        print(f"BrokenPipeError: {e}. Skipping to the next iteration.")
        continue
    except sr.UnknownValueError:
        print(f"Google Web Speech API could not recognize speech in cut{i + 1}. Skipping to the next iteration.")
        continue
    except Exception as e:
        print(f"An error occurred: {e} for cut{i + 1}. Skipping to the next iteration.")
        continue
    finally:
        # Close the audio file
        clip.audio.reader.close_proc()

# Create a document to store the extracted texts.
l_chunks = [diz['chunk{}'.format(i + 1)] for i in range(len(diz))]
text = '\n'.join(l_chunks)

with open('recognized.txt', mode='w') as file:
    file.write("Recognized Speech:")
    file.write("\n")
    file.write(text)
    print("Finally ready!")
