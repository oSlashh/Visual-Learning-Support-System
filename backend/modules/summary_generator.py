import os
import json
import nltk

# Resolve directories dynamically
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_INCOMING_DIR = os.path.join(BACKEND_DIR, 'uploads', 'incoming')
UPLOAD_CACHE_DIR = os.path.join(BACKEND_DIR, 'uploads', 'cache')

def generate_summary(stored_filename: str) -> dict:
    """
    Loads raw text and concepts from caches, ranks sentences using a normalized
    concept-frequency scoring system, structures study notes into an overview
    and ordered key points, and caches the results to cache/<uuid>/summary.json.
    
    Args:
        stored_filename (str): The unique UUID filename (e.g. uuid.pdf).
        
    Returns:
        dict: A structured summary dictionary containing "overview" and "keyPoints".
        
    Raises:
        FileNotFoundError: If raw text or concept cache files are missing.
        ValueError: If extraction or formatting fails.
    """
    base_uuid = stored_filename.rsplit('.', 1)[0]
    
    # 1. Resolve cache paths
    raw_txt_path = os.path.join(UPLOAD_INCOMING_DIR, f"{base_uuid}.txt")
    concepts_json_path = os.path.join(UPLOAD_CACHE_DIR, base_uuid, 'concepts.json')
    
    if not os.path.exists(raw_txt_path):
        raise FileNotFoundError("Raw document text cache is missing. Process the file first.")
    if not os.path.exists(concepts_json_path):
        raise FileNotFoundError("Document concepts cache is missing. Extract concepts first.")
        
    try:
        # Load raw text
        with open(raw_txt_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        # Load concepts
        with open(concepts_json_path, 'r', encoding='utf-8') as f:
            concepts_data = json.load(f)
            
        concepts = concepts_data.get("concepts", [])
        
        # 2. Tokenize sentences using NLTK
        sentences = nltk.sent_tokenize(raw_text)
        
        scored_sentences = []
        for index, sentence in enumerate(sentences):
            # Clean up whitespace/newline artifacts
            clean_sentence = " ".join(sentence.strip().split())
            
            # Skip very short sentences to avoid title / header fragments
            if len(clean_sentence) < 35 or len(clean_sentence.split()) < 6:
                continue
                
            # Score sentence based on concept presence weighted by importance
            score = 0.0
            for concept in concepts:
                term = concept['text'].lower()
                importance = concept['importance']
                # Count frequency of concept term inside the sentence
                occurrences = clean_sentence.lower().count(term)
                score += occurrences * importance
                
            scored_sentences.append({
                "index": index,
                "text": clean_sentence,
                "score": score
            })
            
        if not scored_sentences:
            raise ValueError("No valid sentences could be scored for summary generation.")
            
        # 3. Sort sentences by importance score
        sorted_by_score = sorted(scored_sentences, key=lambda x: x['score'], reverse=True)
        
        # Pick the highest scoring sentence overall to serve as the overview summary
        overview_item = sorted_by_score[0]
        overview_text = overview_item['text']
        
        # Pick the next top 3 highest-scoring sentences as key revision points
        key_points_candidates = sorted_by_score[1:4] if len(sorted_by_score) >= 4 else sorted_by_score[1:]
        
        # Sort key points candidates by their original document index to maintain reading order
        key_points_candidates.sort(key=lambda x: x['index'])
        key_points_text = [item['text'] for item in key_points_candidates]
        
        # In case the document has only 1 sentence scored (fallback)
        if not key_points_text:
            key_points_text = [overview_text]
            
        summary_payload = {
            "summary": {
                "overview": overview_text,
                "keyPoints": key_points_text
            }
        }
        
        # 4. Cache structured summary inside: cache/<uuid>/summary.json
        doc_cache_dir = os.path.join(UPLOAD_CACHE_DIR, base_uuid)
        os.makedirs(doc_cache_dir, exist_ok=True)
        
        summary_json_path = os.path.join(doc_cache_dir, 'summary.json')
        with open(summary_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(summary_payload, json_file, ensure_ascii=False, indent=2)
            
        return summary_payload
        
    except Exception as e:
        raise ValueError(f"Failed to generate study summary: {str(e)}")
