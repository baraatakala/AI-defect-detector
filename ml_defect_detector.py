"""
Advanced ML-powered defect detection using transformers
This module provides BERT-based classification as an upgrade from rule-based detection
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import pickle
import os

class MLDefectClassifier:
    """
    Machine Learning defect classifier using BERT-like transformers
    """
    
    def __init__(self, model_path=None):
        self.model_path = model_path or "models/defect_classifier"
        self.tokenizer = None
        self.model = None
        self.label_encoder = None
        self.defect_categories = [
            'Cracks', 'Damp', 'Corrosion', 'Mold', 
            'Structural', 'Electrical', 'Plumbing'
        ]
        
    def load_pretrained_model(self):
        """Load a pre-trained model or use DistilBERT as base"""
        try:
            # Try to load custom trained model
            if os.path.exists(self.model_path):
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            else:
                # Fall back to base DistilBERT for demo
                self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    'distilbert-base-uncased', 
                    num_labels=len(self.defect_categories)
                )
            print("✅ ML model loaded successfully")
            return True
        except Exception as e:
            print(f"⚠️ ML model not available: {e}")
            return False
    
    def classify_text(self, text):
        """
        Classify text using ML model
        Returns: list of defects with confidence scores
        """
        if not self.model or not self.tokenizer:
            return None
            
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        defects = []
        
        for sentence in sentences[:10]:  # Limit for performance
            try:
                # Tokenize and predict
                inputs = self.tokenizer(
                    sentence, 
                    return_tensors="pt", 
                    truncation=True, 
                    padding=True, 
                    max_length=128
                )
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    
                # Get top prediction
                confidence, predicted_class = torch.max(predictions, 1)
                confidence_score = confidence.item()
                
                # Only include high-confidence predictions
                if confidence_score > 0.7:
                    defect_type = self.defect_categories[predicted_class.item()]
                    severity = self._determine_severity(sentence, confidence_score)
                    
                    defects.append({
                        'type': defect_type,
                        'sentence': sentence,
                        'confidence': confidence_score,
                        'severity': severity,
                        'method': 'ML'
                    })
                    
            except Exception as e:
                continue
                
        return defects
    
    def _determine_severity(self, text, confidence):
        """Determine severity based on text and confidence"""
        text_lower = text.lower()
        
        high_severity_words = ['critical', 'severe', 'dangerous', 'urgent', 'immediate']
        medium_severity_words = ['significant', 'notable', 'concern', 'problem']
        
        if any(word in text_lower for word in high_severity_words) or confidence > 0.9:
            return 'High'
        elif any(word in text_lower for word in medium_severity_words) or confidence > 0.8:
            return 'Medium'
        else:
            return 'Low'

class HybridDefectDetector:
    """
    Combines rule-based and ML approaches for robust defect detection
    """
    
    def __init__(self):
        self.ml_classifier = MLDefectClassifier()
        self.ml_available = self.ml_classifier.load_pretrained_model()
        
    def detect_defects_hybrid(self, text, use_ml=True):
        """
        Detect defects using both rule-based and ML approaches
        """
        defects = []
        
        # Always use rule-based as fallback
        rule_based_defects = self._rule_based_detection(text)
        defects.extend(rule_based_defects)
        
        # Add ML predictions if available
        if use_ml and self.ml_available:
            try:
                ml_defects = self.ml_classifier.classify_text(text)
                if ml_defects:
                    # Merge and deduplicate
                    defects = self._merge_detections(defects, ml_defects)
                    
            except Exception as e:
                print(f"ML detection failed, using rule-based: {e}")
        
        return defects
    
    def _rule_based_detection(self, text):
        """Original rule-based detection as fallback"""
        defect_keywords = {
            'Cracks': ['crack', 'cracked', 'cracking', 'fissure', 'split', 'fracture'],
            'Damp': ['damp', 'moisture', 'wet', 'humidity', 'condensation', 'water damage'],
            'Corrosion': ['corrosion', 'rust', 'corroded', 'oxidation', 'deterioration'],
            'Mold': ['mold', 'mould', 'fungus', 'mildew', 'spores'],
            'Structural': ['structural', 'foundation', 'beam', 'support', 'load-bearing'],
            'Electrical': ['electrical', 'wiring', 'circuit', 'outlet', 'switch'],
            'Plumbing': ['plumbing', 'pipe', 'leak', 'drainage', 'blockage']
        }
        
        detected_defects = []
        text_lower = text.lower()
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        
        for defect_type, keywords in defect_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            detected_defects.append({
                                'type': defect_type,
                                'keyword': keyword,
                                'sentence': sentence.strip(),
                                'severity': 'Medium',
                                'method': 'Rule-based'
                            })
                            break
        
        return detected_defects
    
    def _merge_detections(self, rule_based, ml_based):
        """Merge rule-based and ML detections, prioritizing ML"""
        merged = []
        
        # Add ML detections first (higher priority)
        for ml_defect in ml_based:
            ml_defect['confidence'] = ml_defect.get('confidence', 0.8)
            merged.append(ml_defect)
        
        # Add rule-based detections that don't overlap
        for rule_defect in rule_based:
            # Check if similar defect already detected by ML
            overlap = False
            for ml_defect in ml_based:
                if (rule_defect['type'] == ml_defect['type'] and 
                    rule_defect['sentence'].lower() in ml_defect['sentence'].lower()):
                    overlap = True
                    break
            
            if not overlap:
                rule_defect['confidence'] = 0.7  # Lower confidence for rule-based
                merged.append(rule_defect)
        
        return merged

# Example usage function
def enhanced_detect_defects(text):
    """
    Enhanced defect detection with ML + rule-based hybrid approach
    """
    detector = HybridDefectDetector()
    return detector.detect_defects_hybrid(text, use_ml=True)
