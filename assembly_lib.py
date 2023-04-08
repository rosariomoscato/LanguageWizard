'''
This file is a library for connecting to AssemblyAI via API.
'''

import requests
import os
import time

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

auth_key = os.getenv('API_KEY')

CHUNK_SIZE = 5242880

headers = {
  'Authorization': auth_key,
  'Content-Type': 'application/json'
}


def read_file(filename):
  with open(filename, 'rb') as _file:
    while True:
      data = _file.read(CHUNK_SIZE)
      if not data:
        break
      yield data


def call_assembly(filename):
  """
  Upload a file to AssemblyAI an gets its transcription as string.
  Automatic Language Detection works for the following languages: 
  English, Spanish, French, German, Italian, Portuguese, Dutch.
  """
  upload_response = requests.post(
    upload_endpoint, 
    headers = headers,
    data = read_file(filename)
  )
  
  audio_url = upload_response.json()['upload_url']
  #print("uploaded to:", audio_url)

  transcription_request = {
    "audio_url" : audio_url,
    "iab_categories": True,
    "language_detection": True,
    "entity_detection": True,
    "content_safety": True
    #"summarization": True, # not compatible language_detection
    #"summary_model": "informative", # conversational | catchy
    #"summary_type": "bullets" # paragraph | headline | gist
    }
  
  transcription_response = requests.post(transcript_endpoint, 
                                         json = transcription_request, 
                                         headers = headers)
  
  transcript_id = transcription_response.json()['id']
  polling_endpoint = transcript_endpoint + '/' + transcript_id
  #transcription_state = 'submitted'
  while True:
    polling_response = requests.get(polling_endpoint, headers = headers)
    if polling_response.json()['status'] == 'completed':
      transcription = polling_response.json()['text']
      lang = polling_response.json()['language_code']
      entities = polling_response.json()['entities']
      topics = polling_response.json()['iab_categories_result']['summary']
      content = polling_response.json()['content_safety_labels']["summary"]
      #print("Topics:",topics)
      break
    elif polling_response.json()['status'] == 'error':
      transcription = "error"
      lang = "error"
      entities = "error"
      topics = "error"
      content = "error"
      break
      
    time.sleep(5)
    
  return transcription, lang, entities, topics, content


def call_assembly_en(filename):
  """
  Upload a file to AssemblyAI an gets its transcription as string.
  Automatic Language Detection works for the following languages: 
  English, Spanish, French, German, Italian, Portuguese, Dutch.
  """
  upload_response = requests.post(
    upload_endpoint, 
    headers = headers,
    data = read_file(filename)
  )
  
  audio_url = upload_response.json()['upload_url']
  #print("uploaded to:", audio_url)

  transcription_request = {
    "audio_url" : audio_url,
    "iab_categories": True,
    "entity_detection": True,
    "content_safety": True,
    "summarization": True, # not compatible language_detection
    "summary_model": "informative", # conversational | catchy
    "summary_type": "bullets", # paragraph | headline | gist
    "sentiment_analysis": True
    }
  
  transcription_response = requests.post(transcript_endpoint, 
                                         json = transcription_request, 
                                         headers = headers)
  
  transcript_id = transcription_response.json()['id']
  polling_endpoint = transcript_endpoint + '/' + transcript_id
  #transcription_state = 'submitted'
  while True:
    polling_response = requests.get(polling_endpoint, headers = headers)
    if polling_response.json()['status'] == 'completed':
      transcription = polling_response.json()['text']
      summary = polling_response.json()['summary']
      sentiments = polling_response.json()['sentiment_analysis_results']
      language = polling_response.json()['language_code']
      entities = polling_response.json()['entities']
      topics = polling_response.json()['iab_categories_result']['summary']
      content = polling_response.json()['content_safety_labels']["summary"]
      #print(polling_response.json())
      break
    elif polling_response.json()['status'] == 'error':
      transcription = "error"
      summary = "error"
      sentiments = "error"
      entities = "error"
      topics = "error"
      content = "error"
      break
      
    time.sleep(5)
    
  return transcription, summary, sentiments, entities, topics, content, language
