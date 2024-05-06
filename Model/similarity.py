from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import *
from .GPT import GPT

phobert = AutoModel.from_pretrained(phobert_model_name)
tokenizer = AutoTokenizer.from_pretrained(phobert_model_name)

def similarity(question):
    """
    This function is used to calculate the similarity between question tags and places tags
    and sort them in descending order
    """
    #Get the tags of places and question
    question_tags = GPT(question)
    
    #Tokenize and encode
    result = suggest_destination(question_tags, top_n=top_n)
    
    # Extract features using PhoBERT
    
    return result

def suggest_destination(question_tags, top_n = 5):
    '''
    input: tags is extracted from the question. Ex: question_tags = ['ĐỊA_ĐIỂM DU_LỊCH BIỂN SAN_HÔ BƠI_LỘI CÁT ĐÁ VUI_CHƠI TRẺ_EM']
           data of the destination: destination_1.xlsx
    output: top 5 relevant destination according to the tags 
            return DataFrame contain 'name', 'description','image' and 'simi_score'
    '''
    destinations = pd.read_excel(places_data_path)
    vectorizer = CountVectorizer(max_features=10000, stop_words="english")
    tags_vector = vectorizer.fit_transform(destinations["tags"].values.astype('U')).toarray()
    question_vector = vectorizer.transform(question_tags).toarray()
    similarity_matrix = cosine_similarity(tags_vector, question_vector)
    destinations['simi_score'] = similarity_matrix
    destinations = destinations.sort_values(by ='simi_score', ascending=False)
    result = destinations.iloc[:top_n,:]
    return list(result["name"])

if __name__ == "__main__":
    # Print the sorted sentences
    print(similarity(question))
