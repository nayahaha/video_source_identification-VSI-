import os
import sys
import joblib
import pickle
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from sklearn.decomposition import PCA

from video.ftyp import *
from video.moof import *
from video.moov import *
from video.moov_subatom import *
from video.nal_parser import *
from video.featureExtraction import *

AtomDict = {}
boxSequence = []
codec_id = []


def preprocessing(df, features):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    Format_profile = []
    Writing_application = []
    Movie_name = []
    Video_Format_profile = []
    Video_Format_settings = []
    Video_Title = []
    BOX_Sequence = []
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    with open(f'{BASE_DIR}\\pickle\\tokenizer_ExtraTrees.pkl', 'rb') as handle:
        tokenizer = pickle.load(handle)
    # print("Loaded tokenizer with word index", tokenizer.word_index)

    with open(f'{BASE_DIR}\\pickle\\pca_dict_ExtraTrees.pkl', 'rb') as pca_file:
        pca_dict = pickle.load(pca_file)

    with open(f'{BASE_DIR}\\pickle\\feature_sizes_ExtraTrees.pkl', 'rb') as f:
        feature_sizes = pickle.load(f)

    for feature in features:
        max_len = 0
        temp_seq = 0
        temp_X = 0
        for data in df[feature]:
            if data == 'None':
                data = 'nan'
            if feature == "Format_profile":
                text = ''.join(word for word in data)
                Format_profile.append(text)
            if feature == "Writing_application":
                text = ''.join(word.replace('.', ' ') for word in str(data))
                Writing_application.append(text)
            if feature == "Movie_name":
                text = ''.join(word.replace("_", " ") for word in str(data))
                Movie_name.append(text)
            if feature == "Video_Format_profile":
                text = ''.join(word for word in str(data))
                Video_Format_profile.append(text)
            if feature == "Video_Format_settings":
                text = ''.join(word for word in data)
                Video_Format_settings.append(text)
            if feature == "Video_Title":
                text = ''.join(word for word in str(data))
                Video_Title.append(text)
            if feature == 'BOX_Sequence':
                text = ''.join(word for word in data)
                BOX_Sequence.append(text)

        temp_seq = tokenizer.texts_to_sequences(eval(feature))
        # print(temp_seq)
        max_len = max(len(seq) for seq in temp_seq)
        temp_X = pad_sequences(temp_seq, maxlen=max_len)
        globals()[feature + "_df"] = pd.DataFrame(temp_X)

        temp = eval(feature + "_df")
        expected_features = feature_sizes[feature]
        actual_features = temp.shape[1]

        if actual_features < expected_features:
            temp = np.pad(temp, ((0, 0), (expected_features - actual_features, 0)), 'constant')
        elif actual_features > expected_features:
            temp = temp[:, :expected_features]

        pca = pca_dict[feature]

        globals()[feature + '_transform'] = pca.transform(temp)
    x_data = pd.DataFrame(df, columns=['Video_Bitrate', 'Video_Width(Pixels)', 'Audio_Bitrate', 'Video_Height(Pixels)',
                                       'Video_ID', 'Overall_bitrate', 'Video_Matrix_coefficients'])
    for i in features:
        temp = pd.DataFrame(eval(i + "_transform"))
        for data in temp:
            x_data.insert(data, i + str(temp.columns[data]), temp[data])

    print(x_data)
    return x_data


def classify_source(df, model):
    predictions = model.predict(df)

    return predictions


def classify_source_probability(df, model, labels, top_n=3):
    probabilities = model.predict_proba(df)
    predictions = []

    for prob in probabilities:
        top_indices = np.argsort(prob)[-top_n:][::-1]
        top_labels = [(labels[i], prob[i]) for i in top_indices]
        predictions.append(top_labels)

    return predictions


def main(file_path):
    AtomDict = {}
    boxSequence = []
    codec_id = []

    features = ['BOX_Sequence', 'Video_Format_settings', 'Writing_application', 'Video_Format_profile', 'Movie_name',
                'Video_Title', 'Format_profile']
    LABELS = ['Band', 'Discord', 'Kakaotalk', 'Line', 'Messenger', 'QQ', 'Session', 'Signal', 'Slack', 'Snapchat',
              'Teams', 'Telegram', 'viber', 'wechat', 'whatsapp', 'wire']
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_path = f'{BASE_DIR}\\pickle\\classifier_model_ExtraTrees.pkl'
    model = joblib.load(model_path)
    video_path = file_path
    file_name = os.path.basename(video_path)

    codec_check = videoParsing(video_path, AtomDict, boxSequence)
    df = featureExtraction(video_path, AtomDict, codec_check, boxSequence)
    x_data = preprocessing(df, features)

    # predictions = classify_source(x_data, model)
    #
    # for idx, prediction in enumerate(predictions):
    #     source_class = LABELS[prediction]
    #     print(f"{file_name} -> Video predicted class: {source_class}")

    try:    # moov/meta box 
        if "keys" in AtomDict['moov']['meta']:
            for i in range(AtomDict['moov']['meta']['keys']['entry_count']):
                if b'apple' in AtomDict['moov']['meta']['keys'][f'key_value[{i}]']: # Original video taken with an iPhone
                    percent = 1
                    source_class = "Original_iOS"

                    return source_class, percent
    except KeyError:
        pass
    
    try:    # moov/udta/smrd box
        if AtomDict['moov']['udta']['smrd'].get('smrd_value') == b'TRUEBLUE' and AtomDict['moov']['udta']['smta']['saut']:   # Original video taken with an Android devices
            percent = 1
            source_class = "Original_Android"

            return source_class, percent
    except KeyError:
        pass

    predictions = classify_source_probability(x_data, model, LABELS)[0]
    source_class = None
    percent = 0
    for idx, prediction in enumerate(predictions):
        if percent == 0:
            source_class = prediction[0]
            percent = prediction[1]
        elif percent < prediction[1]:
            source_class = prediction[0]
            percent = prediction[1]

    print(f"{file_name} -> Video predicted class: {source_class}, {percent}")

    return source_class, percent

if __name__ == "__main__":
    main()

