# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 21:22:30 2021

@author: cheng
"""
import argparse

from azure.cognitiveservices.speech import SpeechConfig 
from azure.cognitiveservices.speech import SpeechSynthesizer
from azure.cognitiveservices.speech.audio import AudioOutputConfig

from bs4 import BeautifulSoup
import codecs
import deepl 

from nltk import tokenize, FreqDist
## in first run, need to use the following two lines to download 'punkt'
import nltk
nltk.download('punkt')

import operator
import os
import sys


def main():
    '''
    This is the module to 
        - make text to speech using azure
        https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech
        https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?tabs=script%2Cwindowsinstall&pivots=programming-language-python
        - translate the text from the source language into target languages using DeepL
        https://www.deepl.com/en/docs-api/    
    By default
        - the source language is set to German (DE)
        - the first target language is set to Chinese (ZH)
        - the second target language is set to American English (EN-US)
        - the third target language is set to Spanish (ES)
    Note:
        The free version of azure is limited to translating a certain number of sentences each time
        The default number is set to 20 sentences at once
    '''
    
    ###########################################################################
    ## Here is the example of processing the drei_sonnen
    ## Change the file and directory to your own text
    # ebook xhtml file
    file = '../drei_sonnen/input/ebook/B0A21CC98AC249FCAAD73DA115749CE7.xhtml'
    # the folder to save the processed text into word .doc and audio .mp3 
    directory = "../drei_sonnen/output/chapter_1"
    
    desc = "Using microsoft azure speech-service and DeepL APIs for bilingual language learning"
    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument('--file', type=str, default=file, 
                        help='ebook xhtml file')
    parser.add_argument('--directory', type=str, default=directory, 
                        help='directory to store the output files')
    parser.add_argument('--word_file', type=str, default='translation.doc', 
                        help='word file to save the translation')
    parser.add_argument('--source_language', type=str, default='DE', 
                        help='the source language of the text')
    parser.add_argument('--gender', type=str, choices=['Male', 'Female'], default='Male', 
                        help='the gender of the audio speaker (Male/Female)')    
    # DeepL language list https://www.deepl.com/en/docs-api/other-functions/
    parser.add_argument('--first_target_language', type=str, default='ZH', 
                        help='the first target language')
    parser.add_argument('--second_target_language', type=str, default='EN-US', 
                        help='the second target language')
    parser.add_argument('--third_target_language', type=str, default='ES', # change 'ES' to None to deactivate
                        help='the third target language')
    parser.add_argument('--sentence_index', type=int, default=0, 
                        help='the start position (beginning with 0) of the sentences to be processed')
    # The authentification keys of azure and DeepL
    # Set the default to your own keys
    parser.add_argument('--tts_key', type=str, default="insert your own key here", 
                        help='Azure text-to-speech key')
    parser.add_argument('--region', type=str, default="westeurope", 
                        help='Azure text-to-speech region')
    parser.add_argument('--deepl_key', type=str, default="insert your own key here", 
                        help='DeepL text-to-speech key')    
    args = parser.parse_args(sys.argv[1:])
    
    # Make the output directory
    if not os.path.exists(args.directory):
        os.makedirs(args.directory) 
        
    # extract the sentences from the ebook file
    sentences, words = ebook_to_text(args.file)
    
    # write the unique words by frequency in a descending order
    with open(os.path.join(args.directory, 'words.doc'), 'w', encoding='utf-8') as f:
        for key, value in words.items():
            f.write(key + '\n')
            
    ######################## Start the process ################################
    with open(os.path.join(args.directory, 'translation.doc'), 'a', encoding='utf-8') as f:  
               
        count = args.sentence_index
        if count > 0:
            f.write('\n')
            
        for i, sentence in enumerate(sentences):        
            if i in range(args.sentence_index, args.sentence_index+20):
                f.write(str(count)+'\n')
                print(count)                
                f.write(sentence+'\n') # write the original text sentence by sentence
                print(sentence)
                
                # define the audio synthesizer
                path = os.path.join(args.directory, "%04.0f.mp3"%count)
                synthesizer = text_to_speech(lang=args.source_language, gender=args.gender, 
                                             tts_key=args.tts_key, region=args.region, path=path)            
                # start text to speech synthesation
                synthesizer.speak_text_async(sentence)
                
                # translate the text from source language into the target languages
                if args.first_target_language:
                    ZH_sentence = DLtranslator(sentence.strip(),
                                               deepl_key=args.deepl_key,
                                               target_language=args.first_target_language)
                    f.write(ZH_sentence+'\n') # write the translated text sentence by sentence
                    print(ZH_sentence)
                if args.second_target_language:
                    EN_sentence = DLtranslator(sentence.strip(),
                                               deepl_key=args.deepl_key,
                                               target_language=args.second_target_language)
                    f.write(EN_sentence+'\n') 
                    print(EN_sentence)
                if args.third_target_language:
                    EN_sentence = DLtranslator(sentence.strip(), 
                                               deepl_key=args.deepl_key,
                                               target_language=args.third_target_language)
                    f.write(EN_sentence+'\n')
                    print(EN_sentence, '\n')
                
                f.write('\n')                               
                count+=1 # increase the counter      
        f.close()        
                        

def text_to_speech(lang="DE", gender="Male", tts_key=None, region=None, path=None):
    '''
    Parameters
    ----------
    lang : TYPE, str
        DESCRIPTION. The default is "DE".
    gender : TYPE, optional
        DESCRIPTION. The default is "Male".
    path : TYPE, str
        DESCRIPTION. The path to save the audio.
    Returns
    -------
    synthesizer : TYPE
        This is the function to pass the text using speak_text_async(text) method
    '''    
    # give the MS API key and region
    speech_config = SpeechConfig(subscription=tts_key, 
                                 region=region)    
    if lang=="DE":
        speech_config.speech_synthesis_language = "de-DE"               
        if gender=="Male":
            speech_config.speech_synthesis_voice_name ="de-DE-ConradNeural"
        else:
            speech_config.speech_synthesis_voice_name ="de-DE-KatjaNeural"
    elif lang=="ES":
        speech_config.speech_synthesis_language = "es-ES"
        if gender=="Male":
            speech_config.speech_synthesis_voice_name ="es-ES-AlvaroNeural"
        else:
            speech_config.speech_synthesis_voice_name ="es-ES-ElviraNeural"
    ## define your own languages here according to 
    ## https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech
            
    audio_config = AudioOutputConfig(filename=path)    
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    return synthesizer


def ebook_to_text(file):
    '''
    Parameters
    ----------
    file : str
        This is the ebook xhtml file.
    Returns
    -------
    lines : str
        all the sentences extracted from the xhtml file
        each line is a sentence

    '''
    # Note that German and Spanish may be encoded in utf-8
    # While the current python version use unicode as default
    html=codecs.open(file, 'r', 'utf-8')
    soup = BeautifulSoup(html, features="html.parser", from_encoding="utf-8")        
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    # get text    
    text = soup.get_text()  
            
    # Partition the paragraph into sentences and remove multiple space
    _text = tokenize.sent_tokenize(text)           
    neat_text = [" ".join(i.replace('\ufeff\n', '').strip().split()) for i in _text]
              
    # tokenize the text and sort all the words by frequency in a descending order
    _token = " "
    for i in neat_text:
        _token = _token + i
    tokens = tokenize.word_tokenize(_token)
    fdist1 = FreqDist(tokens)
    filtered_word_freq = dict((word, freq) for word, freq in fdist1.items() 
                              if not word.isdigit())    
    words_dic = dict(sorted(filtered_word_freq.items(), 
                           key=operator.itemgetter(0),
                           reverse=False))
           
    return neat_text, words_dic           


def DLtranslator(text, deepl_key=None, target_language="EN-US"):
    '''
    Parameters
    ----------
    text : str
        source text to be translated
    target_language : str
        the language to be translated into
    Returns
    -------
    translated_text : str
        text in the target language

    '''
    translator = deepl.Translator(deepl_key) 
    result = translator.translate_text(text, 
                                       target_lang=target_language) 
    translated_text = result.text
    return translated_text    


if __name__ =="__main__":
    main()
    
    
        
        
            
    