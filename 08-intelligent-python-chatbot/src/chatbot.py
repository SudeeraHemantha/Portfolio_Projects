import os
import json
import re
import random
import logging
import numpy as np

logger = logging.getLogger("chatbot-engine")

# Gracefully import NLTK tokenizers / lemmatizer with zero-dependency fallback
try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
    lemmatizer = WordNetLemmatizer()
    NLTK_AVAILABLE = True
except Exception as e:
    logger.warning(f"NLTK fallback active ({e}). Using native string normalizer.")
    lemmatizer = None
    NLTK_AVAILABLE = False


def clean_tokenize(text: str) -> list:
    """Normalizes string, removes punctuation, and tokenizes into lower-case words."""
    text_clean = re.sub(r"[^\w\s]", "", text.lower())
    if NLTK_AVAILABLE:
        try:
            return nltk.word_tokenize(text_clean)
        except Exception:
            pass
    return text_clean.split()


def lemmatize_word(word: str) -> str:
    """Reduces word to base lemma form."""
    if NLTK_AVAILABLE and lemmatizer:
        try:
            return lemmatizer.lemmatize(word.lower())
        except Exception:
            pass
    w = word.lower()
    for suffix in ["ing", "ly", "ed", "es", "s"]:
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            return w[:-len(suffix)]
    return w


def create_bag_of_words(tokenized_sentence: list, vocabulary: list) -> np.ndarray:
    """Generates binary Bag-of-Words vector (1 if word in vocabulary, 0 otherwise)."""
    sentence_words = [lemmatize_word(w) for w in tokenized_sentence]
    bag = np.zeros(len(vocabulary), dtype=np.float32)
    for idx, word in enumerate(vocabulary):
        if word in sentence_words:
            bag[idx] = 1.0
    return bag


class ChatbotEngine:
    def __init__(self, intents_filepath: str = os.path.join("data", "intents.json")):
        self.intents_filepath = intents_filepath
        self.intents = []
        self.vocabulary = []
        self.tags = []
        self.documents = []
        self.session_contexts = {} # session_id -> context_string
        self.load_intents()

    def load_intents(self):
        """Loads and pre-processes intents dataset into vocabulary and document tuples."""
        if not os.path.exists(self.intents_filepath):
            logger.error(f"Intents file '{self.intents_filepath}' not found.")
            return

        with open(self.intents_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.intents = data.get("intents", [])

        words = []
        tags = []
        documents = []

        for intent in self.intents:
            tag = intent["tag"]
            if tag not in tags:
                tags.append(tag)
            for pattern in intent["patterns"]:
                tokens = clean_tokenize(pattern)
                words.extend(tokens)
                documents.append((tokens, tag))

        words = sorted(list(set([lemmatize_word(w) for w in words])))
        tags = sorted(list(set(tags)))

        self.vocabulary = words
        self.tags = tags
        self.documents = documents
        logger.info(f"Loaded {len(self.intents)} intents, {len(self.vocabulary)} unique words, {len(self.documents)} pattern tuples.")

    def classify_intent(self, user_message: str, session_id: str = "default") -> tuple:
        """
        Classifies user prompt against intent vocabulary using Bag-of-Words similarity.
        Returns: (matched_tag, confidence_score)
        """
        tokens = clean_tokenize(user_message)
        if not tokens:
            return ("unknown", 0.0)

        user_bag = create_bag_of_words(tokens, self.vocabulary)
        user_norm = np.linalg.norm(user_bag)

        best_tag = "unknown"
        max_score = 0.0

        for pattern_tokens, tag in self.documents:
            pattern_bag = create_bag_of_words(pattern_tokens, self.vocabulary)
            pattern_norm = np.linalg.norm(pattern_bag)

            if user_norm > 0 and pattern_norm > 0:
                # Cosine similarity score
                similarity = float(np.dot(user_bag, pattern_bag) / (user_norm * pattern_norm))
            else:
                similarity = 0.0

            if similarity > max_score:
                max_score = similarity
                best_tag = tag

        return (best_tag, round(max_score, 4))

    def get_response(self, user_message: str, session_id: str = "default") -> dict:
        """
        Processes user query, resolves intent, updates context state, and returns response.
        """
        tag, confidence = self.classify_intent(user_message, session_id)
        current_context = self.session_contexts.get(session_id, "")

        # Fallback for low-confidence matches
        if confidence < 0.2:
            return {
                "response": "I'm sorry, I didn't quite understand that. Could you rephrase your question or ask about our services, hours, or pricing?",
                "tag": "fallback",
                "confidence": confidence,
                "context": current_context
            }

        # Find matching intent
        matched_intent = next((i for i in self.intents if i["tag"] == tag), None)
        if not matched_intent:
            return {
                "response": "How can I assist you today?",
                "tag": "general",
                "confidence": confidence,
                "context": current_context
            }

        # Update session context if set
        if matched_intent.get("context_set"):
            self.session_contexts[session_id] = matched_intent["context_set"]
            current_context = matched_intent["context_set"]

        response_text = random.choice(matched_intent["responses"])

        return {
            "response": response_text,
            "tag": tag,
            "confidence": confidence,
            "context": current_context
        }
