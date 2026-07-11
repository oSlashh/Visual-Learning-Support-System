"""
SmartNotes AI

Console prototype developed for the AI Blend for Engineers Project.

Current Features
- PDF Loading
- Text Extraction
- NLP Preprocessing
- Keyword Extraction
- Rule-Based Summarization
- Rule-Based Flashcard Generation

Future Integration
This module is intentionally designed so its functions can later be reused inside
Flask routes for the web application without significant modification.
"""

import os
import sys
import string
from collections import Counter
from typing import List, Tuple, Dict

# Third-party libraries
import pypdf
import nltk

def download_nltk_resources() -> None:
    """
    Silently downloads required NLTK resources (punkt and stopwords) if 
    they are not already present on the system.
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
        # NLTK v3.9+ might require 'punkt_tab' in certain environments
        try:
            nltk.download('punkt_tab', quiet=True)
        except Exception:
            pass

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)


def load_pdf(file_path: str) -> pypdf.PdfReader:
    """
    Opens a PDF file from a given path and returns a pypdf PdfReader object.
    
    Args:
        file_path (str): The system path to the PDF note file.
        
    Returns:
        pypdf.PdfReader: The loaded PDF reader object.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' could not be found.")
    
    return pypdf.PdfReader(file_path)


def extract_text(reader: pypdf.PdfReader) -> List[str]:
    """
    Iterates through all pages in the PDF reader and extracts their text contents.
    
    Args:
        reader (pypdf.PdfReader): The loaded PDF reader object.
        
    Returns:
        List[str]: A list where each element represents raw text from a page.
    """
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        # If the page has text content, append it; otherwise, append empty string
        pages_text.append(text if text else "")
    return pages_text


def preprocess_text(text: str) -> List[str]:
    """
    Performs NLP cleaning on a raw block of text:
    1. Case normalization (converting to lowercase).
    2. Punctuation removal.
    3. Tokenization into individual words using NLTK.
    4. Stopword removal using NLTK's English stopword corpus.
    
    Args:
        text (str): The raw concatenated text of the PDF.
        
    Returns:
        List[str]: A list of cleaned, lowercase words.
    """
    # 1. Lowercase conversion
    lowered_text = text.lower()
    
    # 2. Punctuation removal (replace punctuation with spaces to avoid joining words)
    # E.g., "AI,machine" -> "AI machine"
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    no_punctuation_text = lowered_text.translate(translator)
    
    # 3. Tokenize words using NLTK
    words = nltk.word_tokenize(no_punctuation_text)
    
    # 4. Stopword removal (filtering out common words like 'the', 'is', 'at')
    english_stopwords = set(nltk.corpus.stopwords.words("english"))
    # Also filter out purely numeric values or single characters to keep keywords meaningful
    cleaned_words = [
        word for word in words 
        if word not in english_stopwords and len(word) > 2 and not word.isdigit()
    ]
    
    return cleaned_words


def extract_keywords(cleaned_words: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
    """
    Identifies the most frequent words in the cleaned text list.
    
    Args:
        cleaned_words (List[str]): List of preprocessed words.
        top_n (int): Number of top keywords to return.
        
    Returns:
        List[Tuple[str, int]]: List of tuples containing (keyword, frequency).
    """
    # Counter counts occurrences of each word automatically
    word_counter = Counter(cleaned_words)
    return word_counter.most_common(top_n)


def generate_summary(text: str, top_keywords: List[str], num_sentences: int = 3) -> List[str]:
    """
    Generates a summary using a simple extractive sentence scoring algorithm.
    It splits text into sentences, scores each based on the frequency of top keywords,
    and returns the top sentences while preserving their original reading order.
    
    Args:
        text (str): The raw concatenated document text.
        top_keywords (List[str]): List of identified top keyword strings.
        num_sentences (int): Number of sentences to include in the summary.
        
    Returns:
        List[str]: Extracted summary sentences.
    """
    # Split the raw text into individual sentences
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return []
    
    # If the document has fewer sentences than requested, return all sentences
    if len(sentences) <= num_sentences:
        return [s.strip() for s in sentences]
    
    # Clean up sentence spacing first
    sentences = [s.strip().replace("\n", " ") for s in sentences]
    
    # Score sentences based on keyword matches
    sentence_scores = {}
    for index, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        score = 0
        for keyword in top_keywords:
            # Add to score based on number of times keyword appears in sentence
            score += sentence_lower.count(keyword.lower())
        sentence_scores[index] = score
        
    # Sort indices by score in descending order and slice the top N
    top_indices = sorted(sentence_scores.keys(), key=lambda idx: sentence_scores[idx], reverse=True)[:num_sentences]
    
    # Re-sort indices chronologically to preserve the original document structure and flow
    top_indices.sort()
    
    # Build list of top sentences
    summary_sentences = [sentences[idx] for idx in top_indices]
    return summary_sentences


def generate_flashcards(sentences: List[str]) -> List[Dict[str, str]]:
    """
    Generates basic educational flashcards using rule-based pattern matching.
    It checks for definitional phrases and parses them into Question/Answer pairs.
    
    Args:
        sentences (List[str]): Sentence tokenized list of the document text.
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing "question" and "answer".
    """
    flashcards = []
    # Definitional triggers arranged from most specific to general
    triggers = [" is defined as ", " refers to ", " is a ", " is an ", " is "]
    
    for sentence in sentences:
        # Standardize spaces and remove line breaks
        cleaned_sentence = sentence.replace("\n", " ").strip()
        
        for trigger in triggers:
            if trigger in cleaned_sentence.lower():
                # Split at the first occurrence of the trigger to isolate the concept
                parts = cleaned_sentence.split(trigger, 1)
                concept = parts[0].strip()
                
                # Filter out splits that are too long (not a single concept) or too short
                words_in_concept = concept.split()
                if 1 <= len(words_in_concept) <= 4:
                    # Clean punctuation from the concept title
                    concept_title = concept.rstrip(string.punctuation).title()
                    
                    # Generate Question based on the trigger phrase used
                    if trigger == " refers to ":
                        question = f"What does {concept_title} refer to?"
                    else:
                        question = f"What is {concept_title}?"
                        
                    # The answer is the full context sentence for accuracy
                    answer = cleaned_sentence
                    
                    flashcards.append({
                        "question": question,
                        "answer": answer
                    })
                    # Move to next sentence once we match a rule
                    break
                    
    return flashcards


def format_console_output(pages_count: int, keywords: List[Tuple[str, int]], 
                          summary_sentences: List[str], flashcards: List[Dict[str, str]]) -> str:
    """
    Formats the processed data into a highly readable, attractive console screen layout.
    
    Args:
        pages_count (int): Total pages in the PDF.
        keywords (List[Tuple[str, int]]): Top extracted keywords.
        summary_sentences (List[str]): Extracted summary sentences.
        flashcards (List[Dict[str, str]]): List of generated Q&A pairs.
        
    Returns:
        str: A single formatted layout string ready for terminal display.
    """
    output = []
    border = "=" * 50
    section_divider = "-" * 50
    
    # 1. Main Title Header
    output.append(border)
    output.append("                  SMARTNOTES AI")
    output.append(border)
    output.append("")
    output.append("PDF Loaded Successfully")
    output.append(f"Pages: {pages_count}")
    output.append("")
    
    # 2. Top Keywords Section
    output.append(section_divider)
    output.append("TOP KEYWORDS")
    output.append(section_divider)
    for idx, (word, count) in enumerate(keywords, 1):
        output.append(f"{idx:2d}. {word:<15} (frequency: {count})")
    output.append("")
    
    # 3. Summary Section
    output.append(section_divider)
    output.append("SUMMARY")
    output.append(section_divider)
    if summary_sentences:
        for idx, sentence in enumerate(summary_sentences, 1):
            output.append(f"[{idx}] {sentence}")
    else:
        output.append("No suitable summary sentences could be generated.")
    output.append("")
    
    # 4. Flashcards Section
    output.append(section_divider)
    output.append("FLASHCARDS")
    output.append(section_divider)
    if flashcards:
        # Show top 5 flashcards to avoid cluttering the terminal output
        for idx, card in enumerate(flashcards[:5], 1):
            output.append(f"Card {idx}:")
            output.append(f"  Q: {card['question']}")
            output.append(f"  A: {card['answer']}")
            output.append("")
    else:
        output.append("No definitions found to generate flashcards.")
        output.append("")
        
    # 5. Footer
    output.append(border)
    output.append("Processing Completed Successfully")
    output.append(border)
    
    return "\n".join(output)


def main() -> None:
    """
    Main execution workflow coordinating parsing, preprocessing,
    analysis, and terminal formatting.
    """
    # 1. Silently resolve NLTK packages on startup
    download_nltk_resources()
    
    # 2. Resolve PDF file path from CLI argument or fall back to sample
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "sample_ai.pdf"
        
    # 3. Load PDF file
    try:
        reader = load_pdf(pdf_path)
    except FileNotFoundError as err:
        print(f"Error: {err}")
        print("Please check the file path and try again.")
        sys.exit(1)
    except Exception as err:
        print(f"Error loading PDF: {err}")
        sys.exit(1)
        
    # 4. Extract Text
    pages_text = extract_text(reader)
    full_text = " ".join(pages_text).strip()
    
    # 5. Check if PDF is empty
    if not full_text:
        print(f"Error: The PDF file '{pdf_path}' has no readable text content.")
        sys.exit(1)
        
    # 6. Preprocess Text
    cleaned_words = preprocess_text(full_text)
    
    # 7. Extract Top Keywords
    top_keywords_tuples = extract_keywords(cleaned_words, top_n=10)
    top_keywords_list = [word for word, count in top_keywords_tuples]
    
    # 8. Generate Summary
    summary_sentences = generate_summary(full_text, top_keywords_list, num_sentences=3)
    
    # 9. Tokenize full text into sentences to feed into flashcard generator
    all_sentences = nltk.sent_tokenize(full_text)
    flashcards = generate_flashcards(all_sentences)
    
    # 10. Format and print the final dashboard
    console_report = format_console_output(
        pages_count=len(reader.pages),
        keywords=top_keywords_tuples,
        summary_sentences=summary_sentences,
        flashcards=flashcards
    )
    print(console_report)

if __name__ == "__main__":
    main()
