# ml_defect_detector_simple.py
# Simplified but robust ML defect detector

import re
from datetime import datetime
import json

# Try to import ML libraries with graceful fallback
ML_AVAILABLE = False
try:
    import torch
    from transformers import pipeline
    import numpy as np
    ML_AVAILABLE = True
    print("✅ ML libraries available")
except ImportError as e:
    print(f"⚠️ ML libraries not available: {e}")
    print("Using rule-based detection only")

class SimpleMLDefectDetector:
    """
    Simplified ML defect detector with robust fallback
    """
    
    def __init__(self):
        self.ml_available = ML_AVAILABLE
        self.defect_categories = [
            'Cracks', 'Damp', 'Corrosion', 'Mold', 
            'Structural', 'Electrical', 'Plumbing'
        ]
        
        # Initialize ML model if available
        self.classifier = None
        if self.ml_available:
            try:
                print("🧠 Initializing ML classifier...")
                self.classifier = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1  # Use CPU to avoid GPU issues
                )
                print("✅ ML classifier ready")
            except Exception as e:
                print(f"⚠️ ML classifier failed to load: {e}")
                self.classifier = None
                self.ml_available = False
        
        # Rule-based patterns (always available)
        self.defect_patterns = {
            'Cracks': [
                r'crack[s]?', r'fissure[s]?', r'split[s]?', r'fracture[s]?',
                r'settlement[- ]crack', r'hairline crack', r'structural crack'
            ],
            'Damp': [
                r'damp[ness]?', r'moist[ure]?', r'wet[ness]?', r'humid[ity]?',
                r'water damage', r'condensation', r'moisture buildup'
            ],
            'Corrosion': [
                r'rust[ing]?', r'corros[ion|ive]', r'oxid[ation|ized]',
                r'corroded', r'deterioration', r'metal damage'
            ],
            'Mold': [
                r'mold', r'mould', r'fungus', r'mildew', r'fungal',
                r'spores', r'black spots'
            ],
            'Structural': [
                r'structural', r'foundation', r'beam[s]?', r'support',
                r'deflection', r'settlement', r'load[- ]bearing',
                r'structural stress', r'structural damage'
            ],
            'Electrical': [
                r'electrical', r'wiring', r'circuit', r'outlet[s]?',
                r'panel', r'GFCI', r'electrical fault', r'electrical safety',
                r'power', r'voltage', r'electrical hazard'
            ],
            'Plumbing': [
                r'plumbing', r'pipe[s]?', r'leak[age]?', r'drain[age]?',
                r'water pressure', r'joint connection', r'blockage',
                r'water system', r'drainage system'
            ]
        }
    
    def detect_defects(self, text):
        """
        Main defect detection method combining ML and rule-based approaches
        """
        if not text or len(text.strip()) < 20:
            return []
        
        defects = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            if len(sentence.strip()) < 15:
                continue
            
            # Try ML detection first if available
            ml_results = None
            if self.ml_available and self.classifier:
                ml_results = self._ml_classify_sentence(sentence)
            
            # Always run rule-based detection
            rule_results = self._rule_based_classify(sentence)
            
            # Combine results
            combined_results = self._combine_results(ml_results, rule_results, sentence)
            defects.extend(combined_results)
        
        return defects
    
    def _split_into_sentences(self, text):
        """Split text into meaningful sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 15]
    
    def _ml_classify_sentence(self, sentence):
        """Classify sentence using ML if available"""
        if not self.classifier:
            return None
        
        try:
            # Use sentiment analysis as a proxy for defect detection confidence
            result = self.classifier(sentence)
            
            # Convert sentiment to defect confidence
            # Negative sentiment often indicates problems/defects
            if result[0]['label'] == 'NEGATIVE':
                confidence = result[0]['score']
                # Use rule-based detection to determine specific type
                rule_type = self._get_primary_defect_type(sentence)
                if rule_type:
                    return {
                        'type': rule_type,
                        'confidence': min(0.95, confidence * 1.2),  # Boost ML confidence
                        'method': 'ml_enhanced'
                    }
            
            return None
            
        except Exception as e:
            print(f"ML classification error: {e}")
            return None
    
    def _rule_based_classify(self, sentence):
        """Rule-based classification"""
        results = []
        sentence_lower = sentence.lower()
        
        for defect_type, patterns in self.defect_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence_lower):
                    # Calculate confidence based on pattern specificity
                    confidence = self._calculate_rule_confidence(pattern, sentence_lower)
                    
                    results.append({
                        'type': defect_type,
                        'confidence': confidence,
                        'method': 'rule_based'
                    })
                    break  # Only one match per category per sentence
        
        return results
    
    def _calculate_rule_confidence(self, pattern, sentence):
        """Calculate confidence for rule-based detection"""
        base_confidence = 0.7
        
        # Boost confidence for specific terms
        specificity_boosts = {
            r'structural crack': 0.2,
            r'water damage': 0.2,
            r'electrical hazard': 0.25,
            r'foundation': 0.15,
            r'safety hazard': 0.2
        }
        
        for specific_pattern, boost in specificity_boosts.items():
            if re.search(specific_pattern, sentence):
                base_confidence += boost
                break
        
        return min(0.9, base_confidence)
    
    def _get_primary_defect_type(self, sentence):
        """Get the most likely defect type for a sentence"""
        sentence_lower = sentence.lower()
        
        for defect_type, patterns in self.defect_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence_lower):
                    return defect_type
        
        return None
    
    def _combine_results(self, ml_results, rule_results, sentence):
        """Combine ML and rule-based results intelligently"""
        combined = []
        
        if ml_results and rule_results:
            # ML and rule-based agree - high confidence
            for rule_result in rule_results:
                if rule_result['type'] == ml_results['type']:
                    combined.append({
                        'type': rule_result['type'],
                        'sentence': sentence,
                        'confidence': min(0.95, (ml_results['confidence'] + rule_result['confidence']) / 2 + 0.1),
                        'severity': self._determine_severity(sentence),
                        'detection_method': 'hybrid_ml_rule'
                    })
                else:
                    # Keep both if they disagree
                    combined.append({
                        'type': rule_result['type'],
                        'sentence': sentence,
                        'confidence': rule_result['confidence'],
                        'severity': self._determine_severity(sentence),
                        'detection_method': 'rule_based'
                    })
        
        elif ml_results:
            # Only ML result
            combined.append({
                'type': ml_results['type'],
                'sentence': sentence,
                'confidence': ml_results['confidence'],
                'severity': self._determine_severity(sentence),
                'detection_method': 'ml_only'
            })
        
        elif rule_results:
            # Only rule-based results
            for rule_result in rule_results:
                combined.append({
                    'type': rule_result['type'],
                    'sentence': sentence,
                    'confidence': rule_result['confidence'],
                    'severity': self._determine_severity(sentence),
                    'detection_method': 'rule_based'
                })
        
        return combined
    
    def _determine_severity(self, sentence):
        """Determine severity based on keywords in sentence"""
        sentence_lower = sentence.lower()
        
        high_severity_keywords = [
            'immediate', 'urgent', 'critical', 'dangerous', 'hazard',
            'safety', 'structural damage', 'major', 'severe'
        ]
        
        medium_severity_keywords = [
            'significant', 'moderate', 'attention', 'monitor',
            'repair', 'maintenance'
        ]
        
        for keyword in high_severity_keywords:
            if keyword in sentence_lower:
                return 'High'
        
        for keyword in medium_severity_keywords:
            if keyword in sentence_lower:
                return 'Medium'
        
        return 'Low'

# Simplified wrapper for backwards compatibility
class HybridDefectDetector:
    """Simplified hybrid detector for easy integration"""
    
    def __init__(self):
        self.detector = SimpleMLDefectDetector()
    
    def detect_defects(self, text):
        """Main detection method"""
        return self.detector.detect_defects(text)
    
    def get_capabilities(self):
        """Get system capabilities"""
        return {
            'ml_available': self.detector.ml_available,
            'rule_based_available': True,
            'hybrid_mode': self.detector.ml_available
        }

# Test function
def test_with_sample():
    """Test the detector with sample data"""
    sample_text = """
    The foundation shows visible cracks along the east wall, measuring approximately 2mm wide.
    Significant damp was observed in the basement area with moisture buildup on the concrete walls.
    The electrical wiring in the main panel appears to be corroded, with several connections showing signs of oxidation.
    Mold growth was detected on the north-facing exterior wall.
    """
    
    detector = HybridDefectDetector()
    results = detector.detect_defects(sample_text)
    
    print("\n🔍 Test Results:")
    print(f"Capabilities: {detector.get_capabilities()}")
    print(f"Defects found: {len(results)}")
    
    for i, defect in enumerate(results, 1):
        print(f"{i}. {defect['type']} - {defect['confidence']:.2f} confidence ({defect['detection_method']})")
        print(f"   Sentence: {defect['sentence'][:80]}...")
    
    return results

if __name__ == "__main__":
    test_with_sample()
