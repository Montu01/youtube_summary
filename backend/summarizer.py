def generate_summary(text, max_length=150, min_length=40):
    """
    Generate a summary of the given text.
    
    Args:
        text (str): The text to summarize
        max_length (int): Maximum length of the summary
        min_length (int): Minimum length of the summary
        
    Returns:
        str: The generated summary (2-3 lines)
    """
    try:
        # Create a very concise 2-3 line summary
        concise_summary = extract_concise_summary(text, max_sentences=3)
            
        return concise_summary
        
    except Exception as e:
        print(f"Error in summarization: {e}")
        # Fallback to a simple extractive summarization
        return extract_concise_summary(text, max_sentences=2)

def translate_text(text, target_language="hi"):
    """
    This is a placeholder for translation functionality.
    Due to dependency issues, actual translation is disabled.
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (e.g., 'hi' for Hindi)
        
    Returns:
        str: Original text with a note
    """
    return f"[Translation to {target_language} is temporarily unavailable. Original text:] {text}"

def split_text(text, max_chunk_size=1000):
    """Split text into chunks of approximately max_chunk_size characters."""
    words = text.split()
    chunks = []
    current_chunk = []
    
    current_size = 0
    for word in words:
        current_size += len(word) + 1  # +1 for space
        if current_size > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word) + 1
        else:
            current_chunk.append(word)
            
    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def extract_important_sentences(text, num_sentences=5):
    """
    A simple extractive summarization method.
    Returns a selection of sentences from the text as a summary.
    """
    sentences = text.split('.')
    
    # Filter out very short sentences
    valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    
    # If we don't have enough valid sentences, use the original sentences
    if len(valid_sentences) < num_sentences:
        valid_sentences = sentences
    
    # Select sentences evenly distributed throughout the text
    if len(valid_sentences) <= num_sentences:
        selected_sentences = valid_sentences
    else:
        # Take the first sentence, the last sentence, and evenly distributed ones in between
        step = len(valid_sentences) // (num_sentences - 2)
        selected_indices = [0]  # First sentence
        
        # Middle sentences
        for i in range(1, num_sentences - 1):
            index = i * step
            if index < len(valid_sentences):
                selected_indices.append(index)
        
        # Last sentence
        if len(valid_sentences) > 1:
            selected_indices.append(len(valid_sentences) - 1)
        
        # Get unique indices (in case there are duplicates due to rounding)
        selected_indices = sorted(set(selected_indices))
        
        # Get the selected sentences
        selected_sentences = [valid_sentences[i] for i in selected_indices if i < len(valid_sentences)]
    
    # Join the selected sentences back together
    summary = '. '.join(selected_sentences)
    
    # Add a period if it doesn't end with one
    if summary and not summary.endswith('.'):
        summary += '.'
        
    return summary

def extract_concise_summary(text, max_sentences=3):
    """
    Creates a very concise 2-3 line summary by extracting the most important sentences.
    
    Args:
        text (str): The text to summarize
        max_sentences (int): Maximum number of sentences to include
        
    Returns:
        str: A very concise summary
    """
    sentences = text.split('.')
    
    # Filter out very short sentences and duplicates
    valid_sentences = []
    seen_content = set()
    
    for s in sentences:
        s = s.strip()
        # Skip short sentences and duplicates based on content fingerprint
        if len(s) > 30 and s.lower()[:50] not in seen_content:
            valid_sentences.append(s)
            # Add a content fingerprint to avoid similar sentences
            seen_content.add(s.lower()[:50])
    
    # Extract the most informative sentences (first, middle and last)
    if len(valid_sentences) <= max_sentences:
        selected_sentences = valid_sentences[:max_sentences]
    else:
        # Always take the first sentence
        selected_sentences = [valid_sentences[0]]
        
        # If we need more than one sentence, add one from the middle
        if max_sentences >= 2 and len(valid_sentences) > 2:
            middle_idx = len(valid_sentences) // 2
            selected_sentences.append(valid_sentences[middle_idx])
        
        # If we need more than two sentences, add one from the end
        if max_sentences >= 3 and len(valid_sentences) > 3:
            selected_sentences.append(valid_sentences[-1])
    
    # Join sentences and make sure it's not too long
    summary = '. '.join(selected_sentences)
    
    # Add a period if needed
    if summary and not summary.endswith('.'):
        summary += '.'
    
    # If it's still too long, truncate and add ellipsis
    max_chars = 250  # Approximately 2-3 lines
    if len(summary) > max_chars:
        last_period = summary[:max_chars].rfind('.')
        if last_period > 0:
            summary = summary[:last_period+1]
        else:
            # If no period found, cut at a word boundary
            last_space = summary[:max_chars].rfind(' ')
            if last_space > 0:
                summary = summary[:last_space] + '...'
    
    return summary
