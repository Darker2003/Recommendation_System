from torch.nn.functional import cosine_similarity

from config import *
from GPT import GPT

phobert = AutoModel.from_pretrained(phobert_model_name)
tokenizer = AutoTokenizer.from_pretrained(phobert_model_name)

def similarity():
    global phobert, tokenizer, places_data_path, question
    """
    This function is used to calculate the similarity between question tags and places tags
    and sort them in descending order
    """
    #Get the tags of places and question
    place_tags = get_place_tags(places_data_path)
    question_tags = GPT(question)
    
    #Tokenize and encode
    question_tags_tokenize = tokenizer.encode(question_tags, max_length=MAX_LENGTH, padding='max_length', truncation=True)
    place_tags_tokenize = [tokenizer.encode(tag, max_length=MAX_LENGTH, padding='max_length', truncation=True) for tag in place_tags]
    tags_tokenize = torch.tensor([question_tags_tokenize] + place_tags_tokenize)
    
    # Extract features using PhoBERT
    with torch.no_grad():
        features = phobert(tags_tokenize)[0].squeeze(0) # Models outputs are now tuples
    
    # Calculate cosine similarity between questio and each place
    consine_similarity_score = cosine_similarity(features[0:1], features[1:], dim=-1)
    
    # Zip the similarity scores with the place
    similarity_score = list(zip(consine_similarity_score.squeeze().tolist(), place_tags))
    
    # Sort the pairs based on the similarity scores in descending order
    similarity_score_sorted = sorted(similarity_score, key=lambda x: x[0], reverse=True)
    place_tags_sorted = [tag[1] for tag in similarity_score_sorted]
    
    return place_tags_sorted

if __name__ == "__main__":
    # Print the sorted sentences
    print("Sorted sentences based on cosine similarity to sentence_root:")
    # print(similarity())
    for i, sentence in enumerate(similarity()):
        print(f"{i+1}. {sentence}")
