import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def create_weights():
    destinations = pd.read_excel("./utils/destination_1.xlsx")
    vectorizer = CountVectorizer(max_features=10000, stop_words="english")
    tags_vector = vectorizer.fit_transform(destinations["tags"].values.astype('U')).toarray()
    # Example array
    weights_tags_vector = [[1, 1, 1, 0.8, 1, 0.5, 0.5, 0.2, 0.5, 1, 1, 1, 1, 1, 1, 0.5, 0.5],
                        [1, 1, 1, 1, 0.2, 0.5, 1, 0.8, 1, 0.5, 0.8, 1, 0.5, 0.5],
                        [1, 1, 1, 1, 0.8, 1, 0.5, 0.8, 1, 1, 1, 0.5, 0.5],
                        [1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.5],
                        [1, 1, 1, 1, 1, 0.8, 0.5, 0.5, 0.5, 0.5, 1, 1, 0.8, 0.5, 0.5],
                        [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 0.5, 0.5],
                        [1, 1, 1, 1, 0.5, 1, 0.5, 0.5],
                        [1, 1, 1, 0.8, 0.8, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5],
                        [1, 1, 1, 0.8, 0.8, 0.2, 0.5, 0.5, 0.5, 1, 1, 1, 0.5],
                        [1, 1, 1, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 0.8, 1, 0.5, 0.5, 0.5],
                        [1, 1, 1, 1, 0.2, 0.5, 0.2, 0.8, 0.8, 0.5, 1, 1, 0.5],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.8, 0.5],
                        [1, 1, 1, 0.8, 1, 1, 0.5, 0.8, 0.5, 1, 0.8, 0.8],
                        [1, 1, 1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 1],
                        [1, 0.8, 0.8, 1, 1, 1, 0.5, 0.5, 0.5, 1, 0.5, 0.5],
                        [1, 1, 1, 0.5, 0.5, 0.5, 0.6, 0.5, 0.8],
                        [1, 1, 1, 1, 0.5, 0.8, 1],
                        [1, 1, 1, 1, 1, 1, 0.5, 0.2, 1, 1, 1, 1, 0.5],
                        [1, 1, 1, 0.5, 0.5, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 0.8, 1, 0.5, 0.2, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 0.8, 0.8, 0.5],
                        [1, 1, 1, 1, 0.5, 1, 1, 1, 1, 1, 0.5, 0.5],
                        [1, 1, 1, 0.5, 0.5, 0.5, 1, 1, 0.5, 0.5, 1, 1], 
                        [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 1, 1, 1, 0.5],
                        [1, 1, 1, 0.5, 1, 1, 1, 1, 1, 0.2],
                        [1, 0.5, 1, 1, 1, 0.8, 0.8, 0.5, 1, 1, 1, 1, 0.5, 0.5],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.2, 1, 0.2, 0.5], 
                        [1, 1, 1, 1, 1, 1, 1, 0.8, 0.5, 1, 1, 0.5, 0.5],
                        [1, 1, 1, 1, 1, 0.5, 0.5, 1, 1, 1, 1, 1, 0.5],
                        [1, 1, 1, 1, 1, 1, 1, 1, 0.8, 0.5, 0.8, 0.8, 0.8, 0.5], 
                        [1, 1, 0.5, 0.5, 1, 1, 0.8, 1, 1, 1, 0.5, 0.5, 0.5], 
                        [1, 1, 0.8, 1, 1, 0.5, 0.8, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 0.5, 1, 1, 1, 0.5, 1, 1, 0.5, 0.8, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1]
                        ]
    #Create a weights vector initialized to zero
    weights_vector = np.zeros(tags_vector.shape)
    #Get feature names (vocabulary) from the vectorizer
    feature_names = vectorizer.get_feature_names_out()
    # Map weights to the appropriate positions in the weights_vector
    for i, row in enumerate(destinations["tags"].values):
        tags = row.split()
        for tag, weight in zip(tags, weights_tags_vector[i]):
            index = np.where(feature_names == tag.lower())[0][0]
            weights_vector[i][index] = weight
    np.save('weights_common.npy', weights_vector)
    
def add_weights_to_tags(tags_vector, weights):
    weights_vector = np.load(weights)
    return weights_vector * tags_vector

def customize_weights(rating, destination_name, question_tags, weights = 'homepage/weights/weights_common.npy'):
    '''Function to customize the feedback weights
    Input: rating: the number of the feedback star. Ex: 3 
            Destination name: the name of the destination Ex: BÃI TẮM KÌ CO 
            Question vector: a vector of 0 and 1. Ex: [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            weights: the file path of the weights. Ex: 'weights_common.npy'
    Output: update the weights file in the same directory. Ex: 'weights_common.npy'
    '''
    
    # Load destinations data and initialize vectorizer
    destinations = pd.read_excel("homepage/destination_1.xlsx")
    vectorizer = CountVectorizer(max_features=10000, stop_words="english")
    vectorizer.fit_transform(destinations["tags"].values.astype('U')).toarray()

    question_vector = vectorizer.transform(question_tags).toarray()

    if rating < 4:
        factor = rating / 4 
    elif rating > 4:
        factor = 1 + (rating - 4) / 4  
    else:
        factor = 1 

    customize_question_vector = np.where(question_vector == 1, question_vector * factor, question_vector)
    weights_vector = np.load(weights)
    index = destinations.index[destinations['name'] == destination_name].tolist()

    weights_vector[index] = np.clip(np.where(customize_question_vector != 0,
                                             customize_question_vector * weights_vector[index],
                                             weights_vector[index]),
                                    0, 1)

    np.save(weights, weights_vector)

def suggest_destination(question_tags, file, top_n = 5):
    '''
    input: tags is extracted from the question. Ex: question_tags = ['ĐỊA_ĐIỂM DU_LỊCH BIỂN SAN_HÔ BƠI_LỘI CÁT ĐÁ VUI_CHƠI TRẺ_EM']
           data of the destination: destination_1.xlsx
    output: top 5 relevant destination according to the tags 
            return DataFrame contain 'name', 'description','image' and 'simi_score'
    '''
    destinations = pd.read_excel("homepage\destination_1.xlsx")
    vectorizer = CountVectorizer(max_features=10000, stop_words="english")
    tags_vector = vectorizer.fit_transform(destinations["tags"].values.astype('U')).toarray()
    question_vector = vectorizer.transform(question_tags).toarray()
    weighted_tags_vector = add_weights_to_tags(tags_vector, file)
    similarity_matrix = cosine_similarity(weighted_tags_vector, question_vector)
    destinations['simi_score'] = similarity_matrix
    destinations = destinations.sort_values(by ='simi_score', ascending=False)
    result = destinations.iloc[:top_n,:]
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
    question_tags = ['BIỂN BƠI_LỘI GIA_ĐÌNH TRẢI_NGHIỆM VUI_CHƠI LẶN SAN_HÔ'] 
    result = suggest_destination(question_tags)
    for title, result in result.iterrows():
        print(result['name'], result['simi_score'])
    