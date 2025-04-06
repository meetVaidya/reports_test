import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# Escape Markdown for Telegram
def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# Cosine similarity-based function
def get_most_similar_query(user_input, ref_queries, method="cosine"):
    """
    Finds the query in the reference dataset with the highest similarity to the user input.
    Uses cosine similarity or BM25.

    Args:
        user_input: The user's query string.
        ref_queries: A dictionary with "queries": [{"description": ..., "query": ...}]
        method: "cosine" or "bm25"

    Returns:
        A dictionary: { "description": ..., "query": ... }
    """
    if not ref_queries or "queries" not in ref_queries or not isinstance(ref_queries["queries"], list):
        return None

    corpus = [q["description"] for q in ref_queries["queries"]]
    all_texts = [user_input] + corpus

    if method == "cosine":
        vectorizer = TfidfVectorizer().fit_transform(all_texts)
        similarity_matrix = cosine_similarity(vectorizer[0:1], vectorizer[1:])
        best_idx = np.argmax(similarity_matrix)
    else:
        raise NotImplementedError("Only cosine similarity is implemented.")

    best_match = ref_queries["queries"][best_idx]
    return {
        "description": best_match["description"],
        "query": best_match["query"]
    }

def format_result(result):
    def escape(val):
        return escape_markdown(str(val))

    if isinstance(result, str):
        return escape(result)

    if isinstance(result, list):
        # If list of tuples
        if all(isinstance(row, (list, tuple)) for row in result):
            formatted_rows = []
            for row in result:
                row_str = " | ".join(
                    escape(val.strftime("%Y-%m-%d %H:%M") if isinstance(val, datetime) else val)
                    for val in row
                )
                formatted_rows.append(f"{row_str}")
            return "\n".join(formatted_rows)

        # If simple list
        return "\n".join(f"- {escape(row)}" for row in result)

    elif isinstance(result, dict):
        return "\n".join(f"{escape(k)}: {escape(v)}" for k, v in result.items())

    return escape(str(result))

# Convert query results to DataFrame
def result_to_dataframe(result):
    """Convert query results to pandas DataFrame"""
    if isinstance(result, list):
        # If result is a list of tuples/lists (common SQL result format)
        if all(isinstance(row, (list, tuple)) for row in result):
            # Extract column names if available
            if hasattr(result, 'columns'):
                columns = result.columns
            else:
                # Generate generic column names
                columns = [f"col_{i}" for i in range(len(result[0]))]
            return pd.DataFrame(result, columns=columns)
        else:
            # Simple list - convert to single column DataFrame
            return pd.DataFrame(result, columns=["value"])

    elif isinstance(result, dict):
        # Convert dict to single-row DataFrame
        return pd.DataFrame([result])

    # If result is not easily convertible, return empty DataFrame
    return pd.DataFrame()
