# Text to speech and with automatic translation
 
## make text to speech using azure
https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech        
https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?tabs=script%2Cwindowsinstall&pivots=programming-language-python

## Translate the text from the source language into target languages using DeepL
https://www.deepl.com/en/docs-api/ 

## Default setting
- the source language is set to German (DE)
- the first target language is set to Chinese (ZH)
- the second target language is set to American English (EN-US)
- the third target language is set to Spanish (ES)

## Note:
- the free version of azure is limited to translating a certain number of sentences each time
- the default number is set to 20 sentences at once

## Environment
create environment
```
conda create --name tts
conda activate tts
conda install python==3.7
pip install azure-cognitiveservices-speech
conda install -c anaconda beautifulsoup4
conda install -c anaconda nltk
pip install --upgrade deepl
```
