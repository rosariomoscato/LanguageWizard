# Core Pkgs
import streamlit as st
st.set_page_config(page_title="Language Wizard by RM",page_icon="./imgs/Rosario_Moscato_LAB_120_120.png")
import streamlit.components.v1 as stc

import warnings
from ui_templates import HTML_BANNER, HTML_STICKER, HTML_BANNER_SKEWED, HTML_WRAPPER

# Data Pkgs
import pandas as pd

# Plotting Pkgs
import matplotlib.pyplot as plt
import matplotlib 
matplotlib.use('Agg')

from PIL import Image
import os
import time
import numpy as np
import json

#Prosody Pkgs
import myprosody as mysp

#AssemblyAI Lib
import assembly_lib as alib

#Import Viz libraries
import matplotlib.pyplot as plt

#Import Fxs Libraries
import text_library

#Audio Files Directory" 
c = r"/home/runner/LanguageWizard/myprosody/"
wav_Dir = "/home/runner/LanguageWizard/myprosody/dataset/audioFiles/"
trans_Dir = "/home/runner/LanguageWizard/Transcriptions/"
entities = []
lang = 'en'


@st.cache_resource
def load_image(img):
  im = Image.open(os.path.join(img))
  return im
  

def voice_similarity(p1,p2):
    '''
    Function to check if the voices in 2 wav files are similar
    '''
    c = r"/home/runner/LanguageWizard/myprosody/"

    f0mean_p1 = mysp.myspf0mean(p1,c)
    f0mean_p2 = mysp.myspf0mean(p2,c)
    f0mean_delta = round(abs(f0mean_p1-f0mean_p2),2)
    #st.write("F0 Mean Delta:",f0mean_delta)

    f0sd_p1 = mysp.myspf0sd(p1,c)
    f0sd_p2 = mysp.myspf0sd(p2,c)
    f0sd_delta = round(abs(f0sd_p1-f0sd_p2),2)
    #st.write("F0 SD Delta:",f0sd_delta)

    f0med_p1 = mysp.myspf0med(p1,c)
    f0med_p2 = mysp.myspf0med(p2,c)
    f0med_delta = round(abs(f0med_p1-f0med_p2),2)
    #st.write("F0 MED Delta:",f0med_delta)
    

    f025_p1 = mysp.myspf0q25(p1,c)
    f025_p2 = mysp.myspf0q25(p2,c)
    f025_delta = round(abs(f025_p1-f025_p2),2)
    #st.write("F0 25P Delta:",f025_delta)

    f075_p1 = mysp.myspf0q75(p1,c)
    f075_p2 = mysp.myspf0q75(p2,c)
    f075_delta = round(abs(f075_p1-f075_p2),2)


    features = {'Parameter': ['Mean Delta     ','St.Dev. Delta  ','Median Delta   ', '25th Per. Delta','75th Per. Delta'],
        'Value': [f0mean_delta,f0sd_delta,f0med_delta,f025_delta,f075_delta]
        }

    df_feat = pd.DataFrame(features, columns = ['Parameter', 'Value'])

    if (f0mean_delta + f0med_delta + f0sd_delta) <= 20.0:
        return "VERY HIGH", df_feat
    elif (f0mean_delta + f0med_delta + f0sd_delta) <= 45.0:
        return "HIGH", df_feat
    elif (f0mean_delta + f0med_delta + f0sd_delta) <= 70.0:
        return "MEDIUM", df_feat
    elif (f0mean_delta + f0med_delta + f0sd_delta) <= 100.0:
        return "LOW", df_feat
    else:
        return "VERY LOW", df_feat


def wav_copy(audio_dir_path, uploaded_file):
  '''
  Function to copy a wav file to an audio files directory.
  '''
  # create the directory if it does not exist
  if not os.path.exists(audio_dir_path):
      os.makedirs(audio_dir_path)

  uploaded_filename = uploaded_file.name
  destination_file_path = os.path.join(audio_dir_path, uploaded_filename)
  
  with open(destination_file_path, 'wb') as f:
    f.write(uploaded_file.getvalue())


def plot_distribution(mean, sd, minimum, maximum):
    # Generate some data from a normal distribution
    data = np.random.normal(mean, sd, 1000)
     
    # Create a histogram of the data using Matplotlib
    fig, ax = plt.subplots()
    ax.hist(data, bins=50)
     
    # Add vertical lines for the minimum, maximum, and mean
    ax.axvline(minimum, color='r', linestyle='dashed', linewidth=2)
    ax.axvline(maximum, color='r', linestyle='dashed', linewidth=2)
    ax.axvline(mean, color='g', linestyle='solid', linewidth=2)
     
    # Add a title and labels to the plot
    ax.set_title('Voice Distribution')
    ax.set_xlabel('Hz')
    ax.set_ylabel('Value')
     
    # Plot in Streamlit
    st.pyplot(fig)



def main():

  print("**************************************")
  print("* Language Wizard                    *")
  print("* Voice Analysis tool by:            *")
  print("* Rosario Moscato                    *")
  print("*                                    *")
  print("* 2021-All Rights Reserved           *")
  print("*                                    *")
  print("*                                    *")
  print("*                                    *")
  print("* email:                             *")
  print("* rosariomoscatolab@gmail.com        *")
  print("**************************************")

  # App Logo
  col10, col20, col30 = st.columns([1,3,1])
  with col10:
    st.header("")
  with col20:
   st.image(load_image("logo.png"), use_column_width="auto")
  with col30:
   st.header("")

  with st.expander("Web App to extract information from voice files in few clicks!", expanded=False):
    st.markdown(f"- Upload a wav file") 
    st.markdown(f"- Select 'Prosodic Analysis'")
    st.markdown(f"- Get your results")
    st.markdown(f"- Continue with 'Content Extraction'")
    st.markdown(f"- The function 'Voice Similarity' is still Experimental")
  
  
  st.sidebar.image(load_image('imgs/biovoice2.jpeg'), use_column_width=True)
  
  enter_menu = ["Prosodic Analysis", "Voice Similarity", "English Only", "About"]
  enter_choice = st.sidebar.selectbox("Select a Module",enter_menu)

	#Global variables 
  global c
  #global audio_files_path
  global wav_Dir
  global trans_Dir
  #global entities
  
  
	# Menu "Voice"
  if enter_choice == "Prosodic Analysis":

		#File Uploading
    uploaded_file = st.sidebar.file_uploader("Upload Audio File (Wav)",type=['wav'])

    if uploaded_file is not None:
      wav_copy(wav_Dir, uploaded_file)
      file_details={"Filename":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
      #st.write(file_details)
			
			# Check File Type
      if uploaded_file.type == "audio/x-wav":
        try:
					#Reading Wav File
          bytes_data = uploaded_file.read()
          
					#Playing Wav File
          st.sidebar.write("Click to play: " + file_details['Filename'])
          st.sidebar.audio(bytes_data, format='audio/x-wav')

					#File Name without WAV extension
          p = file_details['Filename'][:-4]
          
					# Prosodic part
          try:
            #f0 mean (global mean of fundamental frequency distribution Hz)
            #st.write(c)
            f0mean = mysp.myspf0mean(p,c)
            #st.write("F0 Mean (global mean in Hz):", f0mean)

						#f0 SD (global standard deviation of fundamental frequency distribution Hz)
            f0sd = mysp.myspf0sd(p,c)
            #st.write("F0 SD (global standard deviation):", f0sd)

						#f0 MD (global median of fundamental frequency distribution Hz)
            f0med = mysp.myspf0med(p,c)
            #st.write("F0 Median (global median in Hz):", f0med)

						#f0 Min (global minimum of fundamental frequency distribution)
            f0min = mysp.myspf0min(p,c)
            #st.write("F0 Minimum (global minimum in Hz):", f0min)

						#f0 Max (global maximum of fundamental frequency distribution Hz)
            f0max = mysp.myspf0max(p,c)
            #st.write("F0 Maximum (global maximum in Hz):", f0max)

						#f0 quan25 (global 25th quantile of fundamental frequency distribution Hz)
            f025 = mysp.myspf0q25(p,c)
            #st.write("F0 25th Quantile (global 25th quantile in Hz):", f025)

						#f0 quan75 (global 75th quantile of fundamental frequency distribution)
            f075 = mysp.myspf0q75(p,c)
            #st.write("F0 75th Quantile (global 75th quantile in Hz):", f075)

            #plot_distribution(f0mean, f0sd, f0min, f0max)

            # Define two columns
            col_1, col_2 = st.columns(2)
               
            # Add content to first column
            with col_1:
              st.write("")
              plot_distribution(f0mean, f0sd, f0min, f0max)
                
            # Add content to second column  
            with col_2:
              st.write("")
              st.write("Mean (global mean in Hz):", f0mean)
              st.write("SD (global standard deviation):", f0sd)
              st.write("Median (global median in Hz):", f0med)
              st.write("Minimum (global minimum in Hz):", f0min)
              st.write("Maximum (global maximum in Hz):", f0max)
              st.write("25th Quantile (global 25th quantile in Hz):", f025)
              st.write("75th Quantile (global 75th quantile in Hz):", f075)

            with st.expander("Gender & Mood"):
              result = mysp.myspgend(p,c)
              st.info(f"Gender: {result[0]}, Mood of speech: {result[1]}" )

            with st.expander("Speech Duration Statistics"):
              #Original Duration (sec total speaking duration with pauses)
              original_duration = mysp.myspod(p,c)
              st.write("Original Duration (total speaking duration with pauses in seconds):", original_duration)
    
    					#Speaking Duration (sec only speaking duration without pauses)
              speaking_duration = mysp.myspst(p,c)
              st.write("Speaking Duration (only speaking duration without pauses in seconds):", speaking_duration)
    
    					#Balance Ratio (speaking duration/original duration)
              balance = mysp.myspbala(p,c)
              st.write("Balance Ratio (Speaking Duration/Original Duration):", balance)
    
    					#Silent Rate
              silent_rate = original_duration - speaking_duration
              st.write("Silence Duration in seconds:", round(silent_rate,2))
    
    					#Number of Syllables
              syllables = mysp.myspsyl(p,c)
              st.write("Number of Syllables:",syllables)

    					#Number of Pauses
              pauses = mysp.mysppaus(p,c)
              st.write("Number of Pauses:", pauses)
    
    					#Rate of Speech (syllables/second)
              speech_rate = mysp.myspsr(p,c)
              st.write("Rate of Speech (syllables/second in Original Duration):", speech_rate)
    
    					#Articulation Rate
              articulation_rate = mysp.myspatc(p,c)
              st.write("Articulation Rate (syllables/second in Speaking Duration):", articulation_rate)

            transc = st.sidebar.checkbox("Transcription and information extraction")
            if transc:
              global entities
              st.write("")
              st.write("")
              st.info("Language Detection & Transcription")
              st.warning("Automatic Language Detection is supported for the following languages: English, Spanish, French, German, Italian, Portuguese, Dutch. Entity Detection is supported only for English.")
            
              transcription, lang, entities, topics, content = alib.call_assembly(os.path.join(wav_Dir,uploaded_file.name))
              st.info("File Transcription")
              st.write(transcription)
              trans_name = (os.path.join(trans_Dir,uploaded_file.name)[:-4] +".txt")
              with open(trans_name, "w") as f:
                f.write(transcription)
                #st.info(f"Transcription File Saved as:{trans_name}")

              if lang == 'en' or lang == 'en_au' or lang == 'en_uk' or lang == 'en_us':
                with st.expander("Entities"):
                  if len(entities) > 0:
                    st.info("Entities detected:")
                    for entity in entities:
                      st.write(f"(Type, Entity): {entity['entity_type']}, {entity['text']}")
                  else:
                     st.warning("No entities detected")

                with st.expander("Sensitive Content"):
                  if len(content) > 0:
                    pretty_content = json.dumps(content, sort_keys=False, indent=4, separators=(',', ': '))
                    st.json(pretty_content)
                  else:
                      st.warning("No sensitive content detected")

                with st.expander("Main Topics"):
                  if len(topics) > 0:
                    pretty_topics = json.dumps(topics, sort_keys=False, indent=4, separators=(',', ': '))
                    st.json(pretty_topics)
                  else:
                     st.warning("No topics detected")

          except:
            st.write("ERRORE")	

        except:
          st.warning("Problem in loading Audio File...")
              


	# Enter Menu "Similarity"
  elif enter_choice == "Voice Similarity":
    
    st.write("")
    st.write("")
    st.info("Voice Similarity by Prosodic Analisys (Experimental Feature)")
    
    similarity_files = st.file_uploader("Select 2 Audio File (Wav)",type=['wav'], accept_multiple_files=True)
    if similarity_files:
      if len(similarity_files) == 2:
      
        similarity_name_1 = similarity_files[0].name
        similarity_name_2 = similarity_files[1].name
        similarity_name_1 = similarity_name_1[:-4]
        similarity_name_2 = similarity_name_2[:-4]
        wav_copy(wav_Dir, similarity_files[0])
        wav_copy(wav_Dir, similarity_files[1])
        
        result, df_res = voice_similarity(similarity_name_1,similarity_name_2)

        # App Logo
        col1, col2 = st.columns(2)
        with col1:
          st.header("FFDs Comparison")
          st.dataframe(df_res)
        with col2:
          st.header("Similarity Rate")
          output = "Voice Similarity is: " + result
          if result == "VERY HIGH" or result == "HIGH":
            st.success(output)
          elif result == "MEDIUM":
            st.warning(output)
          else:
            st.error(output)
      
      else:
        st.warning("Select 2 Wav files, please.")

  
	# Menu "English Only"
  elif enter_choice == "English Only":
#File Uploading
    uploaded_file = st.sidebar.file_uploader("Upload Audio File (Wav)",type=['wav'])

    if uploaded_file is not None:
      wav_copy(wav_Dir, uploaded_file)
      file_details={"Filename":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
      #st.write(file_details)
			
			# Check File Type
      if uploaded_file.type == "audio/x-wav":
        try:
					#Reading Wav File
          bytes_data = uploaded_file.read()
          
					#Playing Wav File
          st.sidebar.write("Click to play: " + file_details['Filename'])
          st.sidebar.audio(bytes_data, format='audio/x-wav')

					#File Name without WAV extension
          p = file_details['Filename'][:-4]
          
					# Prosodic part
          try:
            #f0 mean (global mean of fundamental frequency distribution Hz)
            #st.write(c)
            f0mean = mysp.myspf0mean(p,c)
            #st.write("F0 Mean (global mean in Hz):", f0mean)

						#f0 SD (global standard deviation of fundamental frequency distribution Hz)
            f0sd = mysp.myspf0sd(p,c)
            #st.write("F0 SD (global standard deviation):", f0sd)

						#f0 MD (global median of fundamental frequency distribution Hz)
            f0med = mysp.myspf0med(p,c)
            #st.write("F0 Median (global median in Hz):", f0med)

						#f0 Min (global minimum of fundamental frequency distribution)
            f0min = mysp.myspf0min(p,c)
            #st.write("F0 Minimum (global minimum in Hz):", f0min)

						#f0 Max (global maximum of fundamental frequency distribution Hz)
            f0max = mysp.myspf0max(p,c)
            #st.write("F0 Maximum (global maximum in Hz):", f0max)

						#f0 quan25 (global 25th quantile of fundamental frequency distribution Hz)
            f025 = mysp.myspf0q25(p,c)
            #st.write("F0 25th Quantile (global 25th quantile in Hz):", f025)

						#f0 quan75 (global 75th quantile of fundamental frequency distribution)
            f075 = mysp.myspf0q75(p,c)
            #st.write("F0 75th Quantile (global 75th quantile in Hz):", f075)

            #plot_distribution(f0mean, f0sd, f0min, f0max)

            # Define two columns
            col_1, col_2 = st.columns(2)
               
            # Add content to first column
            with col_1:
              st.write("")
              plot_distribution(f0mean, f0sd, f0min, f0max)
                
            # Add content to second column  
            with col_2:
              st.write("")
              st.write("Mean (global mean in Hz):", f0mean)
              st.write("SD (global standard deviation):", f0sd)
              st.write("Median (global median in Hz):", f0med)
              st.write("Minimum (global minimum in Hz):", f0min)
              st.write("Maximum (global maximum in Hz):", f0max)
              st.write("25th Quantile (global 25th quantile in Hz):", f025)
              st.write("75th Quantile (global 75th quantile in Hz):", f075)

            with st.expander("Gender & Mood"):
              result = mysp.myspgend(p,c)
              st.info(f"Gender: {result[0]}, Mood of speech: {result[1]}" )

            with st.expander("Speech Duration Statistics"):
              #Original Duration (sec total speaking duration with pauses)
              original_duration = mysp.myspod(p,c)
              st.write("Original Duration (total speaking duration with pauses in seconds):", original_duration)
    
    					#Speaking Duration (sec only speaking duration without pauses)
              speaking_duration = mysp.myspst(p,c)
              st.write("Speaking Duration (only speaking duration without pauses in seconds):", speaking_duration)
    
    					#Balance Ratio (speaking duration/original duration)
              balance = mysp.myspbala(p,c)
              st.write("Balance Ratio (Speaking Duration/Original Duration):", balance)
    
    					#Silent Rate
              silent_rate = original_duration - speaking_duration
              st.write("Silence Duration in seconds:", round(silent_rate,2))
    
    					#Number of Syllables
              syllables = mysp.myspsyl(p,c)
              st.write("Number of Syllables:",syllables)

    					#Number of Pauses
              pauses = mysp.mysppaus(p,c)
              st.write("Number of Pauses:", pauses)
    
    					#Rate of Speech (syllables/second)
              speech_rate = mysp.myspsr(p,c)
              st.write("Rate of Speech (syllables/second in Original Duration):", speech_rate)
    
    					#Articulation Rate
              articulation_rate = mysp.myspatc(p,c)
              st.write("Articulation Rate (syllables/second in Speaking Duration):", articulation_rate)

            transc = st.sidebar.checkbox("Transcription, Summary, Sentiment, etc.")
            if transc:
              #global entities
              st.write("")
              st.write("")
            
              transcription, summary, sentiments, entities, topics, content, lang = alib.call_assembly_en(os.path.join(wav_Dir,uploaded_file.name))
              #print(lang[:2])
              if lang[:2] == "en":
                
                st.info("Transcription")
                st.write(transcription)
                trans_name = (os.path.join(trans_Dir,uploaded_file.name)[:-4] +".txt")
                with open(trans_name, "w") as f:
                  f.write(transcription)
                  #st.info(f"Transcription File Saved as:{trans_name}")
  
                if len(summary) > 0:
                  st.info("Summary")
                  st.write(summary)
  
                with st.expander("Sentiment"):
                  if len(sentiments) > 0:
                    for sent in sentiments:
                      if len(sent['text'])>10:
                        st.write(f"(Text, Sentiment): {sent['text']}, {sent['sentiment']}")
                  else:
                    st.warning("No sentimment detected")
  
                with st.expander("Entities"):
                  if len(entities) > 0:
                    st.info("Entities detected:")
                    for entity in entities:
                      st.write(f"(Type, Entity): {entity['entity_type']}, {entity['text']}")
                  else:
                     st.warning("No entities detected")
  
                with st.expander("Sensitive Content"):
                  if len(content) > 0:
                    pretty_content = json.dumps(content, sort_keys=False, indent=4, separators=(',', ': '))
                    st.json(pretty_content)
                  else:
                    st.warning("No sensitive content detected")
  
                with st.expander("Main Topics"):
                  if len(topics) > 0:
                    pretty_topics = json.dumps(topics, sort_keys=False, indent=4, separators=(',', ': '))
                    st.json(pretty_topics)
                  else:
                     st.warning("No topics detected")
              else:
                st.warning("Language not supported, please submit an English file")


          except:
            st.write("ERRORE")	

        except:
          st.warning("Problem in loading Audio File...")


	# ENDING TEXT PART ---------------------------------------------------------------------------

	# Menu "About"
  else:    
  	stc.html(HTML_STICKER,width=700,height=800)



if __name__ == '__main__':
	main()


