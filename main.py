import subprocess
import os
import io
from pydub import AudioSegment, silence
from pydub.silence import split_on_silence


from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from google.cloud import translate

from google.cloud import texttospeech

import shutil
import contextlib

from audio_text import transcribe_streaming


def converttowav(file):
    command = "ffmpeg -i " + \
        str(file) + " -ac 1 -ar 16000 -acodec pcm_s16le -vn audio.wav"
    subprocess.call(command, shell=True)


def speechtotext(file_name, lang_code):

    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = os.path.join(
        os.path.dirname(__file__),
        file_name)
    # print(file_name)
    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=lang_code)

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    # print(response)
    s = ''
    os.chdir('..')
    with open('audiototext.txt', 'a+', encoding='utf8') as f:
        for result in response.results:
            text = str(result.alternatives[0].transcript)
            f.write(text+'. ')
            s += text

    return s


def translatefunction(string, target):
    # Instantiates a client
    translate_client = translate.Client()

    # target = 'hi'

    # Translates some text into Russian
    translation = translate_client.translate(
        string,
        target_language=target)

    ##print(u'Text: {}'.format(text))
    ##print(u'Translation: {}'.format(translation['translatedText']))
    t = ''
    with open('translated_text.txt', 'a+', encoding='utf8') as f:
        t += str(translation['translatedText'])
        f.write(t+' ')

    return t
    #print("file created")


def translatedspeech(x, language, speaker_type, chunk_num):

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=x)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=language,
        name=speaker_type,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open('chunk'+chunk_num+'.mp3', 'wb+') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        #print('Audio content written to file "output.mp3"')
    out.close()


def silence_based_conversion(path='audio.wav'):

        # open the audio file stored in
        # the local system as a wav file.
    song = AudioSegment.from_wav(path)

    silent = silence.detect_silence(song,
                                    min_silence_len=500,
                                    silence_thresh=-25)
    print(silent)
    #speak = transcribe_streaming('audio.wav')
    #print(speak)

    # split track where silence is 0.5 seconds
    # or more and get chunks
    chunks = split_on_silence(song,
                              # must be silent for at least 0.5 seconds
                              # or 500 ms. adjust this value based on user
                              # requirement. if the speaker stays silent for
                              # longer, increase this value. else, decrease it.
                              min_silence_len=500,

                              # consider it silent if quieter than -16 dBFS
                              # adjust this per requirement
                              silence_thresh=-50
                              )

    # move into the directory to
    # store the audio files.
    os.chdir('audio_chunks')
    os.mkdir('language1')
    os.mkdir('language2')

    i = 0
    # process each chunk
    b = []
    
    for chunk in chunks:
        print(len(chunk))
        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration=10)

        # add 0.5 sec silence to beginning and
        # end of audio chunk. This is done so that
        # it doesn't seem abruptly sliced.
        audio_chunk = chunk_silent + chunk + chunk_silent

        # export audio chunk and save it in
        # the current directory.
        print("saving chunk{0}.wav".format(i))
        # specify the bitrate to be 192 k
        os.chdir('language1')
        audio_chunk.export("./chunk{0}.wav".format(i),
                           bitrate='192k', format="wav")

        # the name of the newly created chunk
        filename = 'chunk'+str(i)+'.wav'

        print("Processing chunk "+str(i))

        # get the name of the newly created chunk
        # in the AUDIO_FILE variable for later use.
        file = filename

        t1 = speechtotext(file, 'hi-IN')

        t2 = translatefunction(t1, 'en')

        if(t1 == ''):
            AudioSegment.from_wav("language1/"+file).export("language2/"+file[0:-4]+'.mp3', format="mp3")
            #shutil.copy('language1/'+file, 'language2/')
            b.append(i)
        else:
            os.chdir('language2')
            translatedspeech(t2, 'hi-IN', 'hi-IN-Standard-C', str(i))
            os.chdir('..')
            
        i += 1

    os.chdir('..')
    chunk_silent = AudioSegment.silent(duration=(silent[0][1]-silent[0][0]))
    final_audio = chunk_silent
    # k=0
# for j in range(0,i-1):
# f1=open('audio_chunks/language1/chunk'+j+'.wav')
# f2=open('audio_chunks/language2/chunk'+j+'.wav')
# if(a[k][0]-silent[j][1]>100):
# if(len(f2)<len(f1)):
##                final_audio+=f2+AudioSegment.silent(duration =len(f1)-len(f2))
##            final_audio+= AudioSegment.silent(duration =(silent[j+1][1]-silent[j+1][0])/10)
# final_audio.export("final_audio.wav",bitrate='192k',format="wav")
    

    for j in range(0, i-1):
        silent.append([0,0])
        print(len(final_audio))
        
        f1=AudioSegment.from_file('audio_chunks/language1/chunk'+str(j)+'.wav',format="wav")
        f2=AudioSegment.from_file('audio_chunks/language2/chunk'+str(j)+".mp3",format="mp3")
        # if(a[k][0]-silent[j][1]>100):
        
        if(len(f2) < len(f1)):
            final_audio = final_audio+f2 + AudioSegment.silent(duration=(len(f1)-len(f2)))
            final_audio += AudioSegment.silent(duration=(silent[j+1][1]-silent[j+1][0]))
            
        else:
            final_audio+=f2
##    if(i>len(silent)):
##        for k in range(len(silent)-1,i):
##            final_audio+=AudioSegment.from_file('audio_chunks/language2/chunk'+str(k)+".mp3",format="mp3")
            
        
    final_audio+=AudioSegment.from_file('audio_chunks/language2/chunk'+str(i-1)+".mp3",format="mp3")
    final_audio.export("final_audio.wav", bitrate='192k', format='wav')


if __name__ == "__main__":
    os.mkdir('audio_chunks')
    converttowav('steve.mp4')
    silence_based_conversion()
    
    command = 'ffmpeg -i steve.mp4 -c copy -an steve1.mp4'
    subprocess.call(command, shell=True)

    cmd = 'ffmpeg -y -i final_audio.wav  -r 30 -i steve1.mp4  -filter:a aresample=async=1 -c:a flac -c:v copy steve2.mkv'
    subprocess.call(cmd, shell=True)
