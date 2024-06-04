import os
import sys
import joblib
import pickle
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from sklearn.decomposition import PCA

# 직접 만든 모듈
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
    # 긴 데이터 프레임 생략 없이 출력 설정
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

    with open('.\\pickle\\tokenizer_ExtraTrees.pkl', 'rb') as handle:
        tokenizer = pickle.load(handle)
    # print("Loaded tokenizer with word index", tokenizer.word_index)

    with open('.\\pickle\\pca_dict_ExtraTrees.pkl', 'rb') as pca_file:
        pca_dict = pickle.load(pca_file)

    with open('.\\pickle\\feature_sizes_ExtraTrees.pkl', 'rb') as f:
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
        # 특성 수 맞추기
        expected_features = feature_sizes[feature]
        actual_features = temp.shape[1]

        if actual_features < expected_features:
            # 필요한 경우 열 추가 (앞쪽에 열 추가)
            temp = np.pad(temp, ((0, 0), (expected_features - actual_features, 0)), 'constant')
            # if feature == 'Video_Format_profile':
            #     print(temp)
        elif actual_features > expected_features:
            # 필요한 경우 열 삭제
            temp = temp[:, :expected_features]

        pca = pca_dict[feature]

        globals()[feature + '_transform'] = pca.transform(temp)
    x_data = pd.DataFrame(df, columns=['Video_Bitrate', 'Video_Width(Pixels)', 'Audio_Bitrate', 'Video_Height(Pixels)',
                                       'Video_ID', 'Overall_bitrate', 'Video_Matrix_coefficients'])  # 수치형 데이터 피처
    for i in features:
        temp = pd.DataFrame(eval(i + "_transform"))  # PCA 적용할 때
        for data in temp:
            x_data.insert(data, i + str(temp.columns[data]), temp[data])
    # sys.stdout = open(f'classification_result(dataset)_messenger,snapchat.txt', 'a')
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
    model_path = '.\\pickle\\classifier_model_ExtraTrees.pkl'
    model = joblib.load(model_path)
    video_path = file_path
    file_name = os.path.basename(video_path)

    codec_check = videoParsing(video_path, AtomDict, boxSequence)
    df = featureExtraction(video_path, AtomDict, codec_check, boxSequence)
    x_data = preprocessing(df, features)

    predictions = classify_source(x_data, model)

    # 예측 결과 출력
    for idx, prediction in enumerate(predictions):
        source_class = LABELS[prediction]
        print(f"{file_name} -> Video predicted class: {source_class}")

    return source_class

if __name__ == "__main__":
    main()

