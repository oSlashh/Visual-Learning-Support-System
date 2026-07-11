import os
import json
import string
import nltk

# Resolve directories dynamically
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_INCOMING_DIR = os.path.join(BACKEND_DIR, 'uploads', 'incoming')
UPLOAD_CACHE_DIR = os.path.join(BACKEND_DIR, 'uploads', 'cache')

# Ensure cache directory exists
os.makedirs(UPLOAD_CACHE_DIR, exist_ok=True)

def preprocess_text_cache(stored_filename: str) -> dict:
    """
    Loads raw text cache from Phase 3, runs NLP cleaning operations
    (lowercasing, punctuation stripping, tokenization, stopword filtering),
    saves the list of cleaned tokens as a JSON cache file, and calculates metrics.
    
    Args:
        stored_filename (str): The unique UUID filename on disk (e.g. uuid.pdf).
        
    Returns:
        dict: A dictionary containing 'totalWords', 'meaningfulWords', and 'removedStopwords'.
        
    Raises:
        FileNotFoundError: If the raw text cache file does not exist.
        ValueError: If processing fails.
    """
    # 1. Resolve raw text filepath (.txt file generated in Phase 3)
    base_name = stored_filename.rsplit('.', 1)[0]
    raw_txt_path = os.path.join(UPLOAD_INCOMING_DIR, f"{base_name}.txt")
    
    if not os.path.exists(raw_txt_path):
        raise FileNotFoundError(
            f"The raw text cache for '{stored_filename}' could not be found. "
            "Please process the document first."
        )
        
    try:
        # Load raw text
        with open(raw_txt_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        # 2. Lowercase conversion
        lowered_text = raw_text.lower()
        
        # 3. Punctuation removal (replace punctuation with spaces to avoid merging words)
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        no_punctuation_text = lowered_text.translate(translator)
        
        # 4. Tokenization using NLTK
        all_tokens = nltk.word_tokenize(no_punctuation_text)
        total_tokens_count = len(all_tokens)
        
        # 5. Stopword removal using NLTK
        english_stopwords = set(nltk.corpus.stopwords.words("english"))
        
        # Filter tokens (exclude stopwords, single characters, and pure numbers)
        meaningful_tokens = [
            token for token in all_tokens
            if token not in english_stopwords and len(token) > 2 and not token.isdigit()
        ]
        
        meaningful_count = len(meaningful_tokens)
        removed_stopwords_count = total_tokens_count - meaningful_count
        
        # 6. Save the cleaned tokens list to JSON cache
        cache_json_path = os.path.join(UPLOAD_CACHE_DIR, f"{base_name}_tokens.json")
        with open(cache_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(meaningful_tokens, json_file, ensure_ascii=False, indent=2)
            
        return {
            "totalWords": total_tokens_count,
            "meaningfulWords": meaningful_count,
            "removedStopwords": removed_stopwords_count
        }
        
    except Exception as e:
        raise ValueError(f"Failed to preprocess text: {str(e)}")
