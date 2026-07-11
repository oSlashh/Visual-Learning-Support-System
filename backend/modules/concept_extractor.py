import os
import json
from collections import Counter

# Resolve directories dynamically
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_CACHE_DIR = os.path.join(BACKEND_DIR, 'uploads', 'cache')

# Generic academic filler words to filter out of the results
ACADEMIC_FILLERS = {
    'introduction', 'chapter', 'fundamentals', 'overview', 'lecture', 
    'section', 'concept', 'concepts', 'summary', 'notes', 'course', 
    'topic', 'topics', 'theory', 'definition', 'definitions', 'example', 
    'examples', 'brief', 'study', 'basic', 'basics', 'outline', 'notes'
}

def discover_concepts(stored_filename: str) -> dict:
    """
    Loads preprocessed tokens JSON file, computes the frequency of terms,
    ranks the top 10, calculates a normalized importance score, and caches
    the result inside a nested folder cache/<uuid>/concepts.json.
    
    Args:
        stored_filename (str): The unique UUID filename (e.g. uuid.pdf).
        
    Returns:
        dict: A dictionary in the format {"concepts": [{"text": str, "frequency": int, "importance": float}]}.
        
    Raises:
        FileNotFoundError: If the token JSON cache is not found.
        ValueError: If parsing or saving fails.
    """
    # 1. Resolve token filepath
    base_uuid = stored_filename.rsplit('.', 1)[0]
    token_json_path = os.path.join(UPLOAD_CACHE_DIR, f"{base_uuid}_tokens.json")
    
    if not os.path.exists(token_json_path):
        raise FileNotFoundError(
            f"Preprocessed tokens for '{stored_filename}' could not be found. "
            "Please run the preprocessing engine first."
        )
        
    try:
        # Load tokens from cache
        with open(token_json_path, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
            
        # 2. Filter out academic filler terms (case-insensitive check)
        filtered_tokens = [
            token for token in tokens
            if token.lower() not in ACADEMIC_FILLERS
        ]
        
        # 3. Calculate frequencies
        word_counts = Counter(filtered_tokens)
        top_concepts = word_counts.most_common(10)
        
        # 4. Compute normalized importance score
        # importance = frequency / max_frequency (rounded to 2 decimal places)
        concepts_list = []
        if top_concepts:
            max_frequency = top_concepts[0][1]
            
            for word, freq in top_concepts:
                importance = round(freq / max_frequency, 2)
                # Capitalize words for user presentation (e.g., 'neural network' -> 'Neural Network')
                concepts_list.append({
                    "text": word.title(),
                    "frequency": freq,
                    "importance": importance
                })
                
        result = {"concepts": concepts_list}
        
        # 5. Cache result in nested structure: cache/<uuid>/concepts.json
        doc_cache_dir = os.path.join(UPLOAD_CACHE_DIR, base_uuid)
        os.makedirs(doc_cache_dir, exist_ok=True)
        
        concepts_json_path = os.path.join(doc_cache_dir, 'concepts.json')
        with open(concepts_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=2)
            
        return result
        
    except Exception as e:
        raise ValueError(f"Failed to extract concepts: {str(e)}")
