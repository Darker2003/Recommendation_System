import json

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SALARY_SCALING = {
    1: (-0.2, 0.2), 
    2: (-0.15, 0.15),
    3: (-0.1, 0.1),
    4: (-0.05, 0.05),
    5: (0, 0), 
    6: (0.05, -0.05),
    7: (0.1, -0.1),
    8: (0.15, -0.15),
    9: (0.2, -0.2)
}

# Load the JSON data
with open('homepage/datasets_text.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Prepare sentences and labels
sentences = [item[0] for item in data["annotations"]]
labels = [item[1]['entities'] for item in data["annotations"]]

# Define tags
tags = data["classes"]
# Convert tags to indices
tag2idx = {tag: 0 for idx, tag in enumerate(tags)}
for label in labels:
    for entity in label:
        tag2idx[entity[1]] = tag2idx[entity[1]] + 1
# Sort the dictionary by values
sorted_tags_dict = dict(sorted(tag2idx.items(), key=lambda item: item[1],reverse=True))
sorted_tags = {key: value for key, value in sorted_tags_dict.items()}
sorted_tags = list(sorted_tags)
for i in range(len(sorted_tags)):
    sorted_tags[i] = sorted_tags[i].replace(" ", "_")

destinations = pd.read_excel("homepage\destination_1.xlsx")
destinations.head()
vectorizer = CountVectorizer(max_features=10000, stop_words="english")
tags_vector = vectorizer.fit_transform(destinations["tags"].values.astype('U')).toarray()
tags_vector = tags_vector[1:]
feature_names = vectorizer.get_feature_names_out()

def create_bias_weights_copilot(file_path):
    """
    Creates a weights vector based on predefined bias values for each tag in the destinations.
    
    This function initializes a zero weights vector and maps predefined bias weights to
    the appropriate positions based on the tags present in the destinations dataset.
    The weights vector is then saved as a NumPy file.
    """
    weights_tags_vector = [[1, 0.9, 0.8, 1, 0.7, 1, 0.9, 0.6, 0.9, 0.9, 0.8, 0.7, 0.8, 1, 1],
                        [1, 0.9, 0.8, 1, 0.7, 0.9, 1, 0.9, 0.6, 0.9, 0.9, 0.8, 0.7, 0.8, 1, 0.8, 1],
                        [0.9, 0.8, 1, 0.7, 1, 0.9, 0.9, 0.6, 0.9, 0.9, 0.8, 0.7, 0.8, 1, 1],
                        [1, 0.9, 0.8, 0.7, 1, 0.7, 0.8, 1, 0.9, 0.9, 1, 0.9, 0.6, 0.9, 0.9, 0.8, 0.7, 0.8, 1, 0.8, 1],
                        [1, 0.8, 0.9, 1, 0.7, 0.6, 1, 0.9, 0.9, 0.6, 0.5, 0.9, 0.9, 0.8, 0.7, 1, 1],
                        [0.8, 0.9, 1, 0.8, 1, 0.9, 0.9, 1, 0.9, 0.9, 0.9, 0.8, 1, 1, 1, 1],
                        [0.9, 0.8, 1, 1, 0.9, 0.9, 1, 0.9, 0.9, 0.9, 0.9, 0.8, 1, 1, 1, 1],
                        [0.8, 0.9, 0.8, 1, 0.9, 1, 0.9, 0.9, 0.9, 0.8, 1, 1, 1],
                        [0.8, 0.9, 0.8, 1, 0.9, 1, 0.9, 0.9, 0.9, 0.8, 1, 1, 1],
                        [0.8, 0.7, 1, 0.9, 1, 0.8, 0.7, 0.7, 0.6, 0.8, 0.8, 1],
                        [0.8, 0.7, 1, 0.8, 1, 0.9, 0.7, 0.7, 1],
                        [0.8, 0.7, 1, 1, 0.9, 0.7, 0.7, 1],
                        [0.8, 0.7, 1, 0.8, 1, 0.9, 0.7, 0.9, 1],
                        [0.8, 0.7, 1, 1, 1, 0.7, 0.7, 1],
                        [0.8, 0.7, 1, 1, 1, 0.9, 0.7, 0.7, 1],
                        [0.8, 0.7, 1, 1, 1, 0.9, 0.8, 0.9, 1],
                        [0.9, 0.8, 1, 0.9, 0.8, 0.7, 0.8, 0.8, 1],
                        [0.8, 0.7, 1, 1, 0.9, 0.8, 0.9, 1],
                        [0.8, 1, 1, 0.9, 0.8, 0.7, 0.8, 1],
                        [0.8, 0.7, 1, 0.9, 0.8, 0.7, 0.7, 1],
                        [0.9, 0.8, 1, 1, 0.9, 0.7, 0.8, 0.7, 0.7, 0.8, 0.8, 1],
                        [0.8, 0.7, 1, 1, 0.9, 0.9, 0.8, 1],
                        [0.8, 1, 1, 1, 1, 0.9, 0.8, 0.8, 1],
                        [0.8, 1, 1, 0.8, 0.8, 1],
                        [0.8, 0.7, 1, 1, 1, 0.8, 0.9, 1],
                        [0.8, 0.9, 1, 1, 0.8, 1, 0.7, 0.9, 0.8, 0.7, 0.9, 1, 0.9, 1, 1, 1],
                        [0.8, 0.7, 1, 1, 1, 0.8, 0.9, 1],
                        [0.8, 0.7, 1, 1, 0.9, 0.8, 0.9, 1],
                        [0.8, 0.7, 1, 1, 1, 0.9, 0.8, 0.7, 0.7, 0.6, 0.8, 0.8, 1, 1],
                        [0.8, 0.7, 0.6, 1, 1, 0.9, 0.8, 0.7, 0.7, 0.6, 0.8, 0.8, 1, 1],
                        [0.8, 0.7, 0.6, 1, 1, 1, 0.9, 0.8, 0.7, 0.7, 0.6, 0.8, 0.8, 1, 1], 
                        [0.8, 0.7, 1, 1, 0.9, 0.9, 0.8, 0.7, 0.7, 0.6, 1, 1], 
                        [0.8, 0.7, 0.9, 0.8, 1, 1, 1, 0.9, 0.8, 0.7, 0.7, 0.6, 0.8, 0.8, 1, 1],
                        [0.8, 0.7, 0.6, 0.8, 1, 1, 0.9, 0.8, 0.7, 0.7, 0.6, 0.8, 0.8, 1, 1],
                        [0.8, 0.7, 0.6, 0.8, 1, 1, 1, 0.9, 0.8, 0.7, 0.7, 0.6, 0.8, 0.8, 1, 1],
                        [1, 0.8, 0.9, 0.7, 0.6, 1, 0.9, 0.8, 1, 1, 0.9, 0.8, 0.8, 0.7, 0.9, 0.9, 1, 1],
                        [1, 0.8, 0.9, 0.7, 0.6, 1, 0.9, 0.8, 1, 1, 0.9, 0.7, 0.6, 0.8, 0.8, 0.8, 0.7, 0.9, 0.9, 1, 0.7, 0.6, 1],
                        [0.9, 0.7, 1, 1, 0.8, 0.7, 0.8, 0.8, 0.7, 1, 1, 1, 1, 1]
                        ]
    weights_vector = np.zeros(tags_vector.shape)

    for i, row in enumerate(destinations['tags'][1:].values):
        tags = row.split()
        for tag, weight in zip(tags, weights_tags_vector[i]):
            index = np.where(feature_names == tag.lower())[0][0]
            weights_vector[i][index] = weight
            
    max_freq = max(sorted_tags_dict.values())
    
    for i, row in enumerate(destinations['tags'][1:].values):
        tags = row.split()
        for tag in tags:
            index = np.where(feature_names == tag.lower())[0][0]
            weights_vector[i][index] = f"{(sorted_tags_dict[tag.replace('_', ' ')]/max_freq):.2f}"
            
    np.save(file_path, weights_vector)
    
def registration_weight(salary_choice, weights='homepage/weights/weights_common.npy'):
    '''
    Function to customize the feedback weights based on rating and salary choice.
    Input: rating: the number of the feedback star. Ex: 3 
           destination_name: the name of the destination. Ex: BÃI TẮM KÌ CO 
           salary_choice: the salary choice from SALARY_CHOICE. Ex: "3"
           weights: the file path of the weights. Ex: 'weights_common.npy'
    Output: Update the weights file in the same directory. Ex: 'weights_common.npy'
    '''
    
    weights_vector = np.load(weights)
    binh_dan_scale, cao_cap_scale = SALARY_SCALING[int(salary_choice)]
    
    tags = ["BÌNH_DÂN"]
    question_vector = vectorizer.transform(tags).toarray()
    
    for i in range(weights_vector.shape[0]):
        mask = weights_vector[i] != 0
        weights_vector[i] = np.clip(weights_vector[i] + (question_vector[0] * binh_dan_scale * mask), 0, 1)
    
    tags = ["CAO_CẤP"]
    question_vector = vectorizer.transform(tags).toarray()
    
    for i in range(weights_vector.shape[0]):
        mask = weights_vector[i] != 0
        weights_vector[i] = np.clip(weights_vector[i] + (question_vector[0] * cao_cap_scale * mask), 0, 1)
    
    np.save(weights, weights_vector)
  
def history_weights(question_tags, increment_value=0.05, weights='homepage/weights/weights_common.npy'):
    '''
    Function to update the feedback weights based on question tags by a constant value.
    Input: 
           question_tags: a list of tags. Ex: ["tag1", "tag2"]
           increment_value: the constant value by which to increase the weights. Ex: 0.1
           weights: the file path of the weights. Ex: 'weights_common.npy'
    Output: Updates the weights file in the same directory. Ex: 'weights_common.npy'
    '''
    question_vector = vectorizer.transform(question_tags).toarray()
    weights_vector = np.load(weights)
    
    for i in range(weights_vector.shape[0]):
        mask = weights_vector[i] != 0
        weights_vector[i] = np.clip(weights_vector[i] + (question_vector[0] * increment_value * mask), 0, 1)

    np.save(weights, weights_vector)
    
def customize_weights(rating, destination_name, question_tags, weights = 'homepage/weights/weights_common.npy'):
    '''Function to customize the feedback weights
    Input: rating: the number of the feedback star. Ex: 3 
            Destination name: the name of the destination Ex: BÃI TẮM KÌ CO 
            Question vector: a vector of 0 and 1. Ex: [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            weights: the file path of the weights. Ex: 'weights_common.npy'
    Output: update the weights file in the same directory. Ex: 'weights_common.npy'
    '''
    question_vector = vectorizer.transform(question_tags).toarray()

    customize_question_vector = np.where(question_vector == 1, question_vector * ((rating + 1)/5), question_vector)
    weights_vector = np.load(weights)
    index = destinations.index[destinations['name'] == destination_name].tolist()

    weights_vector[index] = np.clip(np.where(customize_question_vector != 0,
                                             customize_question_vector * weights_vector[index],
                                             weights_vector[index]),
                                    0, 1)

    np.save(weights, weights_vector)
    
def add_weights_to_tags(tags_vector, weights):
    weights_vector = np.load(weights)
    return weights_vector * tags_vector

def suggest_destination(question_tags, file_path, top_n=12):
    des_list = destinations[1:]
    question_vector = vectorizer.transform(question_tags).toarray()

    weighted_tags_vector = add_weights_to_tags(tags_vector, file_path)
    similarity_matrix = cosine_similarity(weighted_tags_vector, question_vector)

    des_list['simi_score']= similarity_matrix
    des_list = des_list[des_list['simi_score'] > 0]
    des_list_sorted = des_list.sort_values(by ='simi_score', ascending=False)
    result = des_list_sorted.iloc[:top_n,:]
    print('Tags extracted from user question:\n', question_tags)
    print('The most relevant destinations is:')
    for title, similarity in result.iterrows():
        print(similarity['name'], similarity['simi_score'])
        
    return result

def compare_and_print_differences(file_to_compare: str, common_weights_file: str = 'homepage/weights/weights_common.npy'):
    """
    Compare weights in the given .npy file with the common weights file and print the differences.

    :param file_to_compare: Path to the .npy file to compare.
    :param common_weights_file: Path to the common weights file. Default is 'weights_common.npy'.
    """
    weights_to_compare = np.load(file_to_compare)
    common_weights = np.load(common_weights_file)

    if weights_to_compare.shape != common_weights.shape:
        print("The two weight matrices have different shapes and cannot be compared directly.")
        print(f"Shape of common_weights: {common_weights.shape}")
        print(f"Shape of weights_to_compare: {weights_to_compare.shape}")
        return

    difference = weights_to_compare - common_weights
    indices = np.where(difference != 0)
    
    if len(indices[0]) == 0:
        print("The weights are identical.")
    else:
        print(f"The weights differ at {len(indices[0])} positions:")
        for row, col in zip(indices[0], indices[1]):
            print(f"Row {row}, Column {col}: common_weights = {common_weights[row, col]}, weights_to_compare = {weights_to_compare[row, col]}")
            
if __name__ == "__main__":
    create_bias_weights_copilot('homepage/weights/weights_common.npy')
