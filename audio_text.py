
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import translate
from google.cloud import texttospeech
import os
import io
from pydub import AudioSegment
global ans

song = AudioSegment.from_wav("audio.wav")
def translatedspeech(x,language,speaker_type):

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=x)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code= language,
        name = speaker_type ,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    return response

def translatefunction(text,target):
    # Instantiates a client
    translate_client = translate.Client()

    # The text to translate
##    f=open("audiototext.txt", encoding="utf8")
##    text=f.read()
    # target = 'hi'

    # Translates some text into Russian
    translation = translate_client.translate(
        text,
        target_language=target)
    return str(translation['translatedText']);

def transcribe_streaming(stream_file):
    """Streams transcription of the given audio file."""
    f=open('google_time.txt','a+')
    client = speech.SpeechClient()

    with io.open(stream_file, 'rb') as audio_file:
        content = audio_file.read()
    stream = [content]
    requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in stream)
    enable_word_time_offsets = True
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        enable_word_time_offsets= enable_word_time_offsets,
        language_code='en-US')
    streaming_config = types.StreamingRecognitionConfig(config=config)

    responses = client.streaming_recognize(streaming_config, requests)
    array=[]
    for response in responses:
        for result in response.results:
            i=0
            a=[]
            a.append((result.result_end_time.seconds)*1000)
            f.write('EndTime: {}'.format(result.result_end_time.seconds)+'\n')
            #print('EndTime: {}'.format(result.result_end_time.seconds))
            alternatives = result.alternatives
            endtime = result.result_end_time.seconds
            for alternative in alternatives:
                starttime = alternative.words[0].start_time.seconds
                f.write(u'Transcript: {}'.format(alternative.transcript)+'\n')
                #print(u'Transcript: {}'.format(alternative.transcript))
                f.write('StartTime: {}'.format(alternative.words[0].start_time.seconds)+'\n\n\n')
                a.insert(0,(alternative.words[0].start_time.seconds)*1000)
                #print('StartTime: {}'.format(alternative.words[0].start_time.seconds))
                translate = translatefunction(alternative.transcript,'hi')
                transpeech = translatedspeech(translate,'hi-IN','hi-IN-Wavenet-A')
            array.append(a)
    f.close()
    return array


##file_name = os.path.join(
##    os.path.dirname(__file__),
##    'audio.wav')
##transcribe_streaming(file_name)
