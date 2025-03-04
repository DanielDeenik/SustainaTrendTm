"""
Document Processor Module for SustainaTrend™

This module handles PDF document processing, text extraction, and analysis
for sustainability reports and ESG disclosures.
"""

import os
import uuid
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# For PDF text extraction
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None
    logging.warning("PyMuPDF not available. PDF text extraction will be limited.")

# For OCR support
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    Image = None
    pytesseract = None
    logging.warning("PyTesseract or PIL not available. OCR support will be disabled.")

# Create upload directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class DocumentProcessor:
    """Handles document processing, extraction, and analysis"""
    
    def __init__(self):
        """Initialize the document processor"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize sustainability metrics patterns
        self.metrics_patterns = {
            'emissions': [
                r'carbon.*emissions', r'CO2', r'greenhouse gas', r'GHG', 
                r'scope [123]', r'carbon.*footprint', r'carbon neutral',
                r'net zero', r'emission.*reduction'
            ],
            'energy': [
                r'renewable energy', r'energy consumption', r'energy efficiency',
                r'solar', r'wind power', r'energy intensity', r'green energy',
                r'energy transition', r'clean energy'
            ],
            'water': [
                r'water usage', r'water consumption', r'water treatment',
                r'water recycled', r'water intensity', r'water management',
                r'water conservation', r'water stress', r'water efficiency'
            ],
            'waste': [
                r'waste management', r'waste generated', r'waste recycled',
                r'circular economy', r'landfill', r'waste diverted', r'recycling',
                r'waste reduction', r'zero waste', r'composting', r'upcycling'
            ],
            'social': [
                r'diversity', r'inclusion', r'employee training', r'health and safety',
                r'human rights', r'community investment', r'gender pay gap', r'DEI',
                r'social impact', r'labor practices', r'employee wellbeing'
            ],
            'governance': [
                r'board diversity', r'ethics', r'anti-corruption', r'governance',
                r'compliance', r'transparency', r'executive compensation',
                r'sustainability committee', r'ESG oversight', r'business ethics'
            ]
        }
        
        # Regulatory frameworks to identify
        self.frameworks = {
            'TCFD': ['TCFD', 'Task Force on Climate-related Financial Disclosures'],
            'GRI': ['GRI', 'Global Reporting Initiative'],
            'SASB': ['SASB', 'Sustainability Accounting Standards Board'],
            'CSRD': ['CSRD', 'Corporate Sustainability Reporting Directive'],
            'EU Taxonomy': ['EU Taxonomy', 'European Union Taxonomy'],
            'SFDR': ['SFDR', 'Sustainable Finance Disclosure Regulation'],
            'CDP': ['CDP', 'Carbon Disclosure Project'],
            'SDGs': ['SDGs', 'Sustainable Development Goals', 'SDG'],
            'IIRC': ['IIRC', 'International Integrated Reporting Council'],
            'ISO': ['ISO 14001', 'ISO 26000', 'ISO 50001']
        }
    
    def process_document(self, file_path: str, use_ocr: bool = False) -> Dict[str, Any]:
        """
        Process a document and extract text
        
        Args:
            file_path: Path to the document file
            use_ocr: Whether to use OCR for scanned documents
            
        Returns:
            Processing result with extracted text and metadata
        """
        try:
            # Extract text from document
            text, page_count = self.extract_text(file_path, use_ocr)
            
            # Basic document analysis
            word_count = len(text.split())
            file_size = os.path.getsize(file_path)
            
            # Return the processing result
            return {
                'success': True,
                'text': text,
                'page_count': page_count,
                'word_count': word_count,
                'file_size': file_size,
                'preview': text[:1000] + '...' if len(text) > 1000 else text
            }
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text(self, file_path: str, use_ocr: bool = False) -> Tuple[str, int]:
        """
        Extract text from a PDF document
        
        Args:
            file_path: Path to the PDF file
            use_ocr: Whether to use OCR for scanned documents
            
        Returns:
            Tuple of (extracted text, page count)
        """
        if not PYMUPDF_AVAILABLE or fitz is None:
            return "PyMuPDF not available. Cannot extract text from PDF.", 0
        
        try:
            doc = fitz.open(file_path)
            text = ""
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                
                # If page has minimal text and OCR is enabled, apply OCR
                if len(page_text.strip()) < 50 and use_ocr and OCR_AVAILABLE and Image is not None and pytesseract is not None:
                    try:
                        pix = page.get_pixmap()
                        img_data = pix.tobytes()
                        
                        # Create PIL Image from bytes - use tuple instead of list for dimensions
                        img = Image.frombytes("RGB", (pix.width, pix.height), img_data)
                        
                        # Apply OCR
                        page_text = pytesseract.image_to_string(img)
                    except Exception as e:
                        self.logger.warning(f"OCR processing failed: {str(e)}")
                        # Keep the original text if OCR fails
                
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            return text, page_count
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            raise
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Analyze the document text for sustainability metrics and insights
        
        Args:
            text: Extracted document text
            
        Returns:
            Analysis results with metrics, frameworks, and insights
        """
        results = {
            'metrics_identified': self._identify_sustainability_metrics(text),
            'frameworks_mentioned': self._identify_frameworks(text),
            'numerical_kpis': self._extract_numerical_kpis(text),
            'summary': self._generate_executive_summary(text)
        }
        
        return results
    
    def _identify_sustainability_metrics(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify sustainability metrics mentioned in the text
        
        Args:
            text: Document text
            
        Returns:
            Dictionary of metrics by category
        """
        text_lower = text.lower()
        results = {}
        
        for category, patterns in self.metrics_patterns.items():
            mentions = []
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    # Get context (50 chars before and after)
                    start = max(0, match.start() - 50)
                    end = min(len(text_lower), match.end() + 50)
                    context = text_lower[start:end]
                    
                    mentions.append({
                        'pattern': pattern,
                        'context': context,
                        'position': match.start()
                    })
            
            results[category] = mentions
            
        return results
    
    def _identify_frameworks(self, text: str) -> Dict[str, int]:
        """
        Identify sustainability frameworks mentioned in the text
        
        Args:
            text: Document text
            
        Returns:
            Dictionary of framework mentions
        """
        text_upper = text.upper()
        results = {}
        
        for framework, keywords in self.frameworks.items():
            mentions = []
            for keyword in keywords:
                positions = [m.start() for m in re.finditer(keyword.upper(), text_upper)]
                mentions.extend(positions)
            
            results[framework] = len(mentions)
            
        return results
    
    def _extract_numerical_kpis(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract numerical KPIs with context from the text
        
        Args:
            text: Document text
            
        Returns:
            List of KPIs with values and context
        """
        # Pattern to find numbers with units
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(%)',  # Percentages
            r'(\d+(?:\.\d+)?)\s*(tons?|t)\s+(?:of\s+)?(?:CO2|carbon)',  # Carbon tonnage
            r'(\d+(?:\.\d+)?)\s*(GWh|kWh|MWh)',  # Energy units
            r'(\d+(?:\.\d+)?)\s*(m3|cubic meters?|liters?|gallons?)',  # Water units
        ]
        
        kpis = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context (100 chars before and after)
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                kpis.append({
                    'value': match.group(1),
                    'unit': match.group(2),
                    'context': context
                })
                
        return kpis
    
    def _generate_executive_summary(self, text: str) -> str:
        """
        Generate an executive summary of the document (simplified version)
        
        Args:
            text: Document text
            
        Returns:
            Executive summary text
        """
        # In a real implementation, this would use OpenAI or another LLM for summarization
        # Here we're creating a simple extractive summary
        
        # Extract paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Filter to relevant paragraphs that contain sustainability terms
        sustainability_terms = [
            'sustainability', 'sustainable', 'ESG', 'environmental', 'social', 'governance',
            'climate', 'carbon', 'emissions', 'renewable', 'water', 'waste', 'diversity'
        ]
        
        relevant_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if len(para) > 30:  # Skip very short paragraphs
                for term in sustainability_terms:
                    if term.lower() in para.lower():
                        relevant_paragraphs.append(para)
                        break
        
        # Limit to a few paragraphs
        selected_paragraphs = relevant_paragraphs[:3]
        
        # If we found relevant paragraphs, return them; otherwise return a default message
        if selected_paragraphs:
            summary = "Summary of key sustainability points:\n\n"
            for i, para in enumerate(selected_paragraphs, 1):
                summary += f"{i}. {para}\n\n"
            return summary
        else:
            return "This document appears to contain limited sustainability-related content based on initial analysis. For a more comprehensive analysis, please use the advanced AI-powered summarization feature."

    def save_uploaded_file(self, file, use_ocr: bool = False) -> Dict[str, Any]:
        """
        Save an uploaded file and process it
        
        Args:
            file: The uploaded file object
            use_ocr: Whether to use OCR for scanned documents
            
        Returns:
            Processing result with file info and extracted text
        """
        try:
            # Generate a unique filename
            filename = f"{uuid.uuid4()}_{file.filename}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            # Save the file
            file.save(filepath)
            
            # Process the document
            result = self.process_document(filepath, use_ocr)
            
            if result['success']:
                # Add file info
                result['file_info'] = {
                    'original_name': file.filename,
                    'saved_name': filename,
                    'path': filepath,
                    'timestamp': datetime.now().isoformat()
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error saving uploaded file: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Instantiate document processor
document_processor = DocumentProcessor()