"""
Enhanced Document Processor for SustainaTrend™ Data Moat

This module extends the base DocumentProcessor with advanced capabilities for
creating a defensible data moat through enriched document analysis and persistent storage.

The processor implements an agentic RAG workflow that:
1. Extracts text and metadata from documents
2. Applies OCR when needed
3. Extracts and normalizes tables
4. Maps content to regulatory frameworks (ESRS/GRI/TCFD)
5. Calculates and standardizes sustainability indicators
6. Stores all enriched data in the database for long-term value
"""

import os
import logging
import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Try to import PyMuPDF for PDF processing
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

# Try to import Tesseract for OCR
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Import our document processor base class
try:
    from frontend.document_processor import DocumentProcessor
    BASE_PROCESSOR_AVAILABLE = True
except ImportError:
    BASE_PROCESSOR_AVAILABLE = False
    
# Import AI connector for AI-powered processing
try:
    from frontend.data_moat.ai_connector import (
        generate_embeddings,
        query_openai,
        is_openai_available,
        store_embeddings_in_pinecone,
        is_pinecone_available
    )
    AI_CONNECTOR_AVAILABLE = True
except ImportError:
    AI_CONNECTOR_AVAILABLE = False

# Import database connector
from frontend.data_moat.db_connector import db_connector

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """Enhanced document processor with data moat capabilities"""
    
    def __init__(self):
        """Initialize the enhanced document processor"""
        self.logger = logging.getLogger(__name__)
        
        # Try to use the base processor
        self.base_processor = None
        if BASE_PROCESSOR_AVAILABLE:
            self.base_processor = DocumentProcessor()
            self.logger.info("Base DocumentProcessor initialized")
        else:
            self.logger.warning("Base DocumentProcessor not available, using limited functionality")
        
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
                r'community engagement', r'human rights', r'labor practices',
                r'gender equality', r'work.*conditions', r'employee benefits'
            ],
            'governance': [
                r'board diversity', r'executive compensation', r'ethics',
                r'corruption', r'compliance', r'governance structure',
                r'risk management', r'stakeholder engagement', r'transparency',
                r'business ethics', r'code of conduct'
            ]
        }
        
        # Framework detection patterns
        self.frameworks = {
            'esrs': [
                r'ESRS', r'European Sustainability Reporting Standards',
                r'ESRS E1', r'ESRS E2', r'ESRS E3', r'ESRS E4', r'ESRS E5',
                r'ESRS S1', r'ESRS S2', r'ESRS S3', r'ESRS S4',
                r'ESRS G1', r'ESRS G2'
            ],
            'csrd': [
                r'CSRD', r'Corporate Sustainability Reporting Directive',
                r'NFRD', r'Non-Financial Reporting Directive'
            ],
            'gri': [
                r'GRI', r'Global Reporting Initiative',
                r'GRI Standard', r'GRI 102', r'GRI 103', r'GRI 200', r'GRI 300', r'GRI 400'
            ],
            'tcfd': [
                r'TCFD', r'Task Force on Climate-related Financial Disclosures',
                r'climate-related financial'
            ],
            'sdg': [
                r'SDG', r'Sustainable Development Goals',
                r'SDG [0-9]', r'Goal [0-9]', r'Global Goals'
            ],
            'sasb': [
                r'SASB', r'Sustainability Accounting Standards Board'
            ],
            'sfdr': [
                r'SFDR', r'Sustainable Finance Disclosure Regulation',
                r'Article 8', r'Article 9'
            ]
        }
    
    def process_document(self, file_path: str, use_ocr: bool = False, 
                        auto_detect_framework: bool = True,
                        document_type: str = 'sustainability_report') -> Dict[str, Any]:
        """
        Process a document with enhanced data moat capabilities
        
        Args:
            file_path: Path to the document file
            use_ocr: Whether to use OCR for scanned documents
            auto_detect_framework: Whether to automatically detect the framework
            document_type: Type of document
            
        Returns:
            Processing result with extracted text, metadata, and data moat enhancements
        """
        try:
            self.logger.info(f"Processing document with enhanced processor: {file_path}")
            
            # Step 1: Extract text and basic metadata using base processor if available
            if self.base_processor:
                base_result = self.base_processor.process_document(file_path, use_ocr)
                
                if not base_result.get('success', False):
                    return base_result
                
                text = base_result.get('text', '')
                page_count = base_result.get('page_count', 0)
                base_metrics = base_result.get('metrics', {})
                base_frameworks = base_result.get('frameworks', {})
                document_structure = base_result.get('document_structure', {})
            else:
                # Fall back to direct extraction
                text, page_count = self.extract_text(file_path, use_ocr)
                base_metrics = self._identify_sustainability_metrics(text)
                base_frameworks = self._identify_frameworks(text)
                document_structure = self._create_document_structure(text, page_count)
            
            # Step 2: Detect if OCR is needed (if not explicitly provided)
            if not use_ocr and self._is_ocr_needed(text, page_count):
                self.logger.info("OCR detected as needed, re-processing with OCR")
                return self.process_document(file_path, use_ocr=True, 
                                           auto_detect_framework=auto_detect_framework,
                                           document_type=document_type)
            
            # Step 3: Prepare metadata for storage
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            metadata = {
                'filename': file_name,
                'file_size': file_size,
                'page_count': page_count,
                'word_count': len(text.split()),
                'processed_time': datetime.now().isoformat(),
                'processor_version': '1.0',
                'ocr_applied': use_ocr
            }
            
            # Step 4: Auto-detect framework if enabled
            detected_frameworks = {}
            if auto_detect_framework:
                detected_frameworks = self._identify_frameworks(text)
                primary_framework = self._get_primary_framework(detected_frameworks)
                metadata['primary_framework'] = primary_framework
                metadata['detected_frameworks'] = detected_frameworks
            
            # Step 5: Store document in database
            document_id = db_connector.store_document(
                content=text,
                document_type=document_type,
                metadata=metadata
            )
            
            if not document_id:
                return {
                    'success': False,
                    'error': 'Failed to store document in database'
                }
            
            # Step 6: Perform enhanced metric extraction
            enhanced_metrics = self._extract_enhanced_metrics(text, document_structure)
            normalized_metrics = self._normalize_metrics(enhanced_metrics)
            
            # Step 7: Create framework mappings with evidence links
            regulatory_mapping = self._create_regulatory_mapping(text, document_structure, detected_frameworks)
            
            # Step 8: Extract tables and normalize them
            tables = self._extract_and_normalize_tables(file_path)
            
            # Step 9: Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(text, enhanced_metrics, regulatory_mapping)
            
            # Step 10: Store enriched data in database
            db_connector.update_document_enrichment(
                document_id=document_id,
                regulatory_mapping=regulatory_mapping,
                extracted_metrics=normalized_metrics,
                document_structure=document_structure,
                confidence_scores=confidence_scores,
                processing_status='processed'
            )
            
            # Step 11: Store standardized metrics mapping
            standardized_metrics = self._convert_to_standardized_metrics(normalized_metrics, document_id)
            db_connector.store_metrics_mapping(
                document_id=document_id,
                metrics=standardized_metrics
            )
            
            # Step 12: Store compliance assessment for each detected framework
            for framework_id, score in detected_frameworks.items():
                if score > 0.3:  # Only store significant framework detections
                    compliance_assessment = self._assess_framework_compliance(text, framework_id, document_structure)
                    db_connector.store_regulatory_compliance(
                        document_id=document_id,
                        framework_id=framework_id,
                        overall_score=compliance_assessment.get('overall_score', 0.0),
                        category_scores=compliance_assessment.get('category_scores', {}),
                        findings=compliance_assessment.get('findings', {}),
                        recommendations=compliance_assessment.get('recommendations', {}),
                        evidence_links=compliance_assessment.get('evidence_links', {})
                    )
            
            # Step 13: Create vector embeddings and store in Pinecone if available
            if AI_CONNECTOR_AVAILABLE and is_pinecone_available():
                self._create_and_store_embeddings(text, document_id, metadata)
            
            # Return the enhanced processing result
            return {
                'success': True,
                'document_id': document_id,
                'text_length': len(text),
                'page_count': page_count,
                'word_count': len(text.split()),
                'file_size': file_size,
                'preview': text[:1000] + '...' if len(text) > 1000 else text,
                'metrics_count': len(standardized_metrics),
                'frameworks_detected': detected_frameworks,
                'primary_framework': metadata.get('primary_framework', ''),
                'tables_extracted': len(tables),
                'confidence_score': confidence_scores.get('overall', 0.0),
                'enrichment_status': 'complete',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error in enhanced document processing: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text(self, file_path: str, use_ocr: bool = False) -> Tuple[str, int]:
        """
        Extract text from a document, with enhanced handling for different file types
        
        Args:
            file_path: Path to the document file
            use_ocr: Whether to use OCR for scanned documents
            
        Returns:
            Tuple of (extracted text, page count)
        """
        # Use base processor if available
        if self.base_processor:
            return self.base_processor.extract_text(file_path, use_ocr)
        
        if not PYMUPDF_AVAILABLE or fitz is None:
            return "PyMuPDF not available. Cannot extract text from PDF.", 0
        
        try:
            doc = fitz.open(file_path)
            text = ""
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                
                if use_ocr and TESSERACT_AVAILABLE:
                    # Use OCR for this page
                    pix = page.get_pixmap()
                    img_path = f"temp_ocr_{page_num}.png"
                    pix.save(img_path)
                    
                    # Process with Tesseract
                    img = Image.open(img_path)
                    page_text = pytesseract.image_to_string(img)
                    
                    # Clean up temporary file
                    os.remove(img_path)
                else:
                    # Use normal text extraction
                    page_text = page.get_text()
                
                text += f"\n\n[Page {page_num + 1}]\n{page_text}"
            
            return text, page_count
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return f"Error extracting text: {str(e)}", 0
    
    def _is_ocr_needed(self, text: str, page_count: int) -> bool:
        """
        Determine if OCR is needed for the document
        
        Args:
            text: Extracted text
            page_count: Number of pages
            
        Returns:
            True if OCR is needed, False otherwise
        """
        # Check if the text is too short for the number of pages
        words_per_page = len(text.split()) / max(page_count, 1)
        
        # Check for common OCR indicators
        has_text = len(text.strip()) > 0
        has_enough_words = words_per_page > 50  # A typical page would have more than 50 words
        
        return (not has_text) or (not has_enough_words and page_count > 3)
    
    def _identify_sustainability_metrics(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify sustainability metrics mentioned in the text with enhanced context
        
        Args:
            text: Document text
            
        Returns:
            Dictionary of metrics by category with enhanced metadata
        """
        # Use base processor if available
        if self.base_processor:
            base_metrics = self.base_processor._identify_sustainability_metrics(text)
            # Enhance the base metrics
            return self._enhance_base_metrics(base_metrics, text)
        
        # Otherwise, do our own processing
        metrics = {}
        text_lower = text.lower()
        
        for category, patterns in self.metrics_patterns.items():
            metrics[category] = []
            
            for pattern in patterns:
                for match in re.finditer(pattern, text_lower):
                    # Get surrounding context (100 chars before and after)
                    start = max(0, match.start() - 100)
                    end = min(len(text_lower), match.end() + 100)
                    context = text_lower[start:end]
                    
                    # Find the full sentence for better context
                    sentence_start = text_lower.rfind('.', 0, match.start())
                    if sentence_start == -1:
                        sentence_start = max(0, match.start() - 200)
                    sentence_end = text_lower.find('.', match.end())
                    if sentence_end == -1:
                        sentence_end = min(len(text_lower), match.end() + 200)
                    sentence = text[sentence_start + 1:sentence_end].strip()
                    
                    # Extract potential value near the match
                    value = self._extract_metric_value(context)
                    
                    # Determine page reference
                    page_ref = self._find_page_reference(text, match.start())
                    
                    metrics[category].append({
                        'match': match.group(0),
                        'context': context,
                        'sentence': sentence,
                        'value': value,
                        'position': match.start(),
                        'page': page_ref,
                        'confidence': 0.8  # Default confidence, will be refined later
                    })
        
        return metrics
    
    def _enhance_base_metrics(self, base_metrics: Dict[str, List[Dict[str, Any]]], text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Enhance base metrics with additional data for the data moat
        
        Args:
            base_metrics: Metrics from the base processor
            text: Document text
            
        Returns:
            Enhanced metrics dictionary
        """
        enhanced_metrics = {}
        
        for category, metrics_list in base_metrics.items():
            enhanced_metrics[category] = []
            
            for metric in metrics_list:
                # Enhanced metric with additional fields
                enhanced_metric = dict(metric)  # Copy the original metric
                
                # Add value extraction if not present
                if 'value' not in enhanced_metric:
                    context = enhanced_metric.get('context', '')
                    enhanced_metric['value'] = self._extract_metric_value(context)
                
                # Add unit extraction if not present
                if 'unit' not in enhanced_metric:
                    enhanced_metric['unit'] = self._extract_metric_unit(enhanced_metric.get('value', ''))
                
                # Add page reference if not present
                if 'page' not in enhanced_metric and 'position' in enhanced_metric:
                    enhanced_metric['page'] = self._find_page_reference(text, enhanced_metric['position'])
                
                # Add year/time period if not present
                if 'year' not in enhanced_metric:
                    enhanced_metric['year'] = self._extract_year_reference(enhanced_metric.get('context', ''))
                
                # Add normalization potential
                enhanced_metric['can_normalize'] = self._can_normalize_metric(enhanced_metric)
                
                # Add confidence score
                if 'confidence' not in enhanced_metric:
                    enhanced_metric['confidence'] = self._calculate_metric_confidence(enhanced_metric)
                
                enhanced_metrics[category].append(enhanced_metric)
        
        return enhanced_metrics
    
    def _extract_metric_value(self, context: str) -> str:
        """
        Extract potential metric value from context
        
        Args:
            context: Context around a metric mention
            
        Returns:
            Extracted value or empty string if not found
        """
        # Look for numbers with optional units
        value_patterns = [
            r'(\d+(?:\.\d+)?(?:\s*[%kMGTPB]?g?CO2e?)?)',  # Numbers with optional units
            r'(\d+(?:\.\d+)?(?:\s*million)?(?:\s*billion)?(?:\s*trillion)?)',  # Numbers with scale
            r'(\d+(?:\.\d+)?(?:\s*percent|perc|pct|%))',  # Percentage values
            r'reduced by (\d+(?:\.\d+)?(?:\s*[%kMGTPB]?))'  # Reduction values
        ]
        
        for pattern in value_patterns:
            matches = re.findall(pattern, context)
            if matches:
                return matches[0]
        
        return ""
    
    def _extract_metric_unit(self, value_str: str) -> str:
        """
        Extract unit from a value string
        
        Args:
            value_str: Value string
            
        Returns:
            Extracted unit or empty string if not found
        """
        # Common sustainability units
        unit_patterns = [
            (r'%', '%'),
            (r'CO2e?', 'CO2e'),
            (r'kgCO2e?', 'kgCO2e'),
            (r'tCO2e?', 'tCO2e'),
            (r'MWh', 'MWh'),
            (r'GWh', 'GWh'),
            (r'kWh', 'kWh'),
            (r'm3', 'm³'),
            (r'million', 'million'),
            (r'billion', 'billion'),
            (r'tons', 'tons'),
            (r'tonnes', 'tonnes')
        ]
        
        for pattern, unit in unit_patterns:
            if re.search(pattern, value_str, re.IGNORECASE):
                return unit
        
        return ""
    
    def _find_page_reference(self, text: str, position: int) -> int:
        """
        Find the page reference for a position in the text
        
        Args:
            text: Document text
            position: Position in the text
            
        Returns:
            Page number (1-based)
        """
        # Look for page markers like [Page X]
        page_markers = re.findall(r'\[Page (\d+)\]', text[:position])
        if page_markers:
            return int(page_markers[-1])
        
        # Fall back to estimation based on average page length
        avg_chars_per_page = 3000  # Approximate
        return max(1, position // avg_chars_per_page + 1)
    
    def _extract_year_reference(self, context: str) -> str:
        """
        Extract year reference from context
        
        Args:
            context: Context around a metric mention
            
        Returns:
            Extracted year or empty string if not found
        """
        # Look for years (2000-2030)
        year_matches = re.findall(r'(20[0-2][0-9])', context)
        if year_matches:
            return year_matches[0]
        
        return ""
    
    def _can_normalize_metric(self, metric: Dict[str, Any]) -> bool:
        """
        Determine if a metric can be normalized
        
        Args:
            metric: Metric data
            
        Returns:
            True if the metric can be normalized, False otherwise
        """
        # Check if we have a numeric value
        value = metric.get('value', '')
        if not value:
            return False
        
        # Try to extract a numeric part
        numeric_matches = re.findall(r'\d+(?:\.\d+)?', value)
        if not numeric_matches:
            return False
        
        # Check if we have a unit
        unit = metric.get('unit', '')
        if not unit:
            return False
        
        return True
    
    def _calculate_metric_confidence(self, metric: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a metric
        
        Args:
            metric: Metric data
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on context quality
        if metric.get('sentence', ''):
            confidence += 0.1
        
        # Increase confidence based on value presence
        if metric.get('value', ''):
            confidence += 0.2
        
        # Increase confidence based on unit presence
        if metric.get('unit', ''):
            confidence += 0.1
        
        # Increase confidence based on year presence
        if metric.get('year', ''):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _extract_enhanced_metrics(self, text: str, document_structure: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract enhanced sustainability metrics with additional context and metadata
        
        Args:
            text: Document text
            document_structure: Structure of the document
            
        Returns:
            Dictionary of enhanced metrics
        """
        # Start with base metrics
        metrics = self._identify_sustainability_metrics(text)
        
        # Use AI for enhanced extraction if available
        if AI_CONNECTOR_AVAILABLE and is_openai_available():
            ai_metrics = self._extract_metrics_with_ai(text)
            
            # Merge AI-extracted metrics with pattern-based metrics
            for category, ai_metrics_list in ai_metrics.items():
                if category not in metrics:
                    metrics[category] = []
                
                # Add new metrics from AI that aren't already in the list
                existing_positions = [m.get('position', -1) for m in metrics[category]]
                for ai_metric in ai_metrics_list:
                    ai_pos = ai_metric.get('position', -1)
                    
                    # Check for duplicates (metrics within 100 chars of each other)
                    is_duplicate = False
                    for pos in existing_positions:
                        if abs(ai_pos - pos) < 100:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        metrics[category].append(ai_metric)
        
        return metrics
    
    def _extract_metrics_with_ai(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract metrics using AI assistance
        
        Args:
            text: Document text
            
        Returns:
            Dictionary of AI-extracted metrics
        """
        if not AI_CONNECTOR_AVAILABLE or not is_openai_available():
            return {}
        
        try:
            # Prepare a prompt for OpenAI
            prompt = f"""
            Extract sustainability metrics from the following document text. 
            Focus on environmental, social, and governance metrics.
            For each metric, extract:
            1. The category (emissions, energy, water, waste, social, governance, biodiversity, circular economy)
            2. The specific metric name
            3. The value and unit (if mentioned)
            4. The year or reporting period
            5. The context (surrounding sentence)
            
            Return as a JSON object with categories as keys and arrays of metrics as values.
            Each metric should include: metric name, value, unit, year, and context.
            
            Document text:
            {text[:10000]}  # Use first 10k chars to stay within token limits
            """
            
            response = query_openai(prompt)
            
            if response and response.get('content'):
                # Parse the JSON response
                try:
                    metrics_json = json.loads(response['content'])
                    
                    # Convert to our format
                    result = {}
                    for category, metrics_list in metrics_json.items():
                        result[category] = []
                        
                        for metric in metrics_list:
                            # Find the position in the text
                            context = metric.get('context', '')
                            position = text.find(context) if context else -1
                            
                            enhanced_metric = {
                                'match': metric.get('metric name', ''),
                                'value': metric.get('value', ''),
                                'unit': metric.get('unit', ''),
                                'year': metric.get('year', ''),
                                'context': context,
                                'position': position,
                                'page': self._find_page_reference(text, position),
                                'confidence': 0.9,  # AI-extracted metrics get higher confidence
                                'source': 'ai'
                            }
                            
                            result[category].append(enhanced_metric)
                    
                    return result
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse AI response as JSON")
                    return {}
            
            return {}
        except Exception as e:
            self.logger.error(f"Error extracting metrics with AI: {str(e)}")
            return {}
    
    def _normalize_metrics(self, metrics: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Normalize metrics for standardized comparison
        
        Args:
            metrics: Raw metrics dictionary
            
        Returns:
            Dictionary of normalized metrics
        """
        normalized = {}
        
        for category, metrics_list in metrics.items():
            normalized[category] = []
            
            for metric in metrics_list:
                normalized_metric = dict(metric)  # Copy the original metric
                
                # Extract numeric value for normalization
                value_str = metric.get('value', '')
                numeric_matches = re.findall(r'\d+(?:\.\d+)?', value_str)
                
                if numeric_matches:
                    # Convert to numeric value
                    try:
                        numeric_value = float(numeric_matches[0])
                        
                        # Apply normalization based on unit
                        unit = metric.get('unit', '').lower()
                        
                        # Scale to base units
                        if 'million' in value_str.lower():
                            numeric_value *= 1_000_000
                        elif 'billion' in value_str.lower():
                            numeric_value *= 1_000_000_000
                        elif 'thousand' in value_str.lower() or 'k' in value_str.lower():
                            numeric_value *= 1_000
                        
                        # Convert units
                        if 'tco2' in unit:
                            normalized_unit = 'tCO2e'
                        elif 'kgco2' in unit:
                            normalized_unit = 'tCO2e'
                            numeric_value /= 1000  # Convert kg to tonnes
                        elif 'gwh' in unit:
                            normalized_unit = 'MWh'
                            numeric_value *= 1000  # Convert GWh to MWh
                        else:
                            normalized_unit = unit
                        
                        normalized_metric['normalized_value'] = numeric_value
                        normalized_metric['normalized_unit'] = normalized_unit
                    except ValueError:
                        # Could not convert to float
                        normalized_metric['normalized_value'] = None
                        normalized_metric['normalized_unit'] = metric.get('unit', '')
                else:
                    normalized_metric['normalized_value'] = None
                    normalized_metric['normalized_unit'] = metric.get('unit', '')
                
                normalized[category].append(normalized_metric)
        
        return normalized
    
    def _identify_frameworks(self, text: str) -> Dict[str, float]:
        """
        Identify sustainability frameworks mentioned in the text
        
        Args:
            text: Document text
            
        Returns:
            Dictionary of framework mentions with confidence scores
        """
        # Use base processor if available
        if self.base_processor:
            return self.base_processor._identify_frameworks(text)
        
        framework_mentions = {}
        text_lower = text.lower()
        
        for framework, patterns in self.frameworks.items():
            mentions = 0
            
            for pattern in patterns:
                # Count mentions of this pattern
                count = len(re.findall(pattern, text, re.IGNORECASE))
                mentions += count
            
            # Calculate a confidence score based on mentions
            if mentions > 0:
                confidence = min(1.0, 0.3 + (mentions / 10) * 0.7)  # Scale from 0.3 to 1.0
                framework_mentions[framework] = confidence
        
        return framework_mentions
    
    def _get_primary_framework(self, frameworks: Dict[str, float]) -> str:
        """
        Determine the primary framework from detected frameworks
        
        Args:
            frameworks: Dictionary of detected frameworks with confidence scores
            
        Returns:
            Primary framework ID
        """
        if not frameworks:
            return 'unknown'
        
        # Return the framework with highest confidence
        return max(frameworks.items(), key=lambda x: x[1])[0]
    
    def _create_document_structure(self, text: str, page_count: int) -> Dict[str, Any]:
        """
        Create a structured representation of the document
        
        Args:
            text: Document text
            page_count: Number of pages
            
        Returns:
            Document structure with sections, headings, and page mappings
        """
        # Use base processor if available
        if self.base_processor:
            return self.base_processor._create_document_structure(text, page_count)
        
        # Simple implementation - extract headings
        structure = {
            'page_count': page_count,
            'sections': [],
            'headings': [],
            'page_map': {}
        }
        
        # Extract page breaks and content
        pages = re.split(r'\[Page \d+\]', text)
        
        for i, page_content in enumerate(pages[1:], 1):  # Skip the first split which is before first [Page X]
            structure['page_map'][i] = {
                'start_position': text.find(f'[Page {i}]'),
                'length': len(page_content),
                'headings': []
            }
        
        # Extract headings - look for capitalized lines that could be headings
        potential_headings = re.findall(r'^([A-Z][A-Z\s\d]{3,60})$', text, re.MULTILINE)
        
        for heading in potential_headings:
            heading_pos = text.find(heading)
            
            # Determine the page for this heading
            heading_page = 1
            for page, page_data in structure['page_map'].items():
                if heading_pos >= page_data['start_position']:
                    heading_page = page
            
            heading_info = {
                'title': heading.strip(),
                'position': heading_pos,
                'page': heading_page
            }
            
            structure['headings'].append(heading_info)
            structure['page_map'][heading_page]['headings'].append(heading_info)
        
        # Create sections from headings
        prev_heading = None
        for i, heading in enumerate(sorted(structure['headings'], key=lambda h: h['position'])):
            if prev_heading:
                section = {
                    'title': prev_heading['title'],
                    'start': prev_heading['position'],
                    'end': heading['position'],
                    'start_page': prev_heading['page'],
                    'end_page': heading['page'],
                    'text': text[prev_heading['position']:heading['position']]
                }
                structure['sections'].append(section)
            
            prev_heading = heading
        
        # Add final section
        if prev_heading:
            section = {
                'title': prev_heading['title'],
                'start': prev_heading['position'],
                'end': len(text),
                'start_page': prev_heading['page'],
                'end_page': page_count,
                'text': text[prev_heading['position']:]
            }
            structure['sections'].append(section)
        
        return structure
    
    def _create_regulatory_mapping(self, text: str, document_structure: Dict[str, Any], 
                                 detected_frameworks: Dict[str, float]) -> Dict[str, Any]:
        """
        Create detailed mapping between document content and regulatory frameworks
        
        Args:
            text: Document text
            document_structure: Document structure
            detected_frameworks: Detected frameworks
            
        Returns:
            Regulatory mapping with evidence links
        """
        regulatory_mapping = {}
        
        # For each detected framework with sufficient confidence
        for framework, confidence in detected_frameworks.items():
            if confidence < 0.3:
                continue  # Skip low-confidence frameworks
            
            framework_mapping = {
                'framework_id': framework,
                'confidence': confidence,
                'matches': []
            }
            
            # For ESRS, map to specific disclosure requirements
            if framework == 'esrs':
                esrs_patterns = {
                    'ESRS E1': r'E1(?:-\d+)?',  # Climate change
                    'ESRS E2': r'E2(?:-\d+)?',  # Pollution
                    'ESRS E3': r'E3(?:-\d+)?',  # Water and marine resources
                    'ESRS E4': r'E4(?:-\d+)?',  # Biodiversity and ecosystems
                    'ESRS E5': r'E5(?:-\d+)?',  # Resource use and circular economy
                    'ESRS S1': r'S1(?:-\d+)?',  # Own workforce
                    'ESRS S2': r'S2(?:-\d+)?',  # Workers in the value chain
                    'ESRS S3': r'S3(?:-\d+)?',  # Affected communities
                    'ESRS S4': r'S4(?:-\d+)?',  # Consumers and end-users
                    'ESRS G1': r'G1(?:-\d+)?',  # Business conduct
                    'ESRS G2': r'G2(?:-\d+)?'   # Governance, risk management and internal control
                }
                
                for requirement, pattern in esrs_patterns.items():
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        # Get context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        
                        # Find page reference
                        page = self._find_page_reference(text, match.start())
                        
                        framework_mapping['matches'].append({
                            'requirement': requirement,
                            'match': match.group(0),
                            'position': match.start(),
                            'page': page,
                            'context': context
                        })
            
            # For GRI, map to specific standards
            elif framework == 'gri':
                gri_patterns = {
                    'GRI 102': r'GRI 102(?:-\d+)?',  # General Disclosures
                    'GRI 103': r'GRI 103(?:-\d+)?',  # Management Approach
                    'GRI 200': r'GRI 2(?:0\d|1\d)(?:-\d+)?',  # Economic
                    'GRI 300': r'GRI 3(?:0\d|1\d|2\d)(?:-\d+)?',  # Environmental
                    'GRI 400': r'GRI 4(?:0\d|1\d|2\d)(?:-\d+)?'   # Social
                }
                
                for standard, pattern in gri_patterns.items():
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        # Get context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        
                        # Find page reference
                        page = self._find_page_reference(text, match.start())
                        
                        framework_mapping['matches'].append({
                            'standard': standard,
                            'match': match.group(0),
                            'position': match.start(),
                            'page': page,
                            'context': context
                        })
            
            # TCFD has four pillars
            elif framework == 'tcfd':
                tcfd_pillars = {
                    'Governance': r'governance',
                    'Strategy': r'strategy',
                    'Risk Management': r'risk management',
                    'Metrics and Targets': r'metrics and targets'
                }
                
                for pillar, pattern in tcfd_pillars.items():
                    for match in re.finditer(r'TCFD.*?' + pattern, text, re.IGNORECASE):
                        # Get context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        
                        # Find page reference
                        page = self._find_page_reference(text, match.start())
                        
                        framework_mapping['matches'].append({
                            'pillar': pillar,
                            'match': match.group(0),
                            'position': match.start(),
                            'page': page,
                            'context': context
                        })
            
            # For other frameworks, just store mentions
            else:
                framework_patterns = self.frameworks.get(framework, [])
                
                for pattern in framework_patterns:
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        # Get context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        
                        # Find page reference
                        page = self._find_page_reference(text, match.start())
                        
                        framework_mapping['matches'].append({
                            'match': match.group(0),
                            'position': match.start(),
                            'page': page,
                            'context': context
                        })
            
            # Add to regulatory mapping
            regulatory_mapping[framework] = framework_mapping
        
        return regulatory_mapping
    
    def _extract_and_normalize_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from the document and normalize them
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of extracted and normalized tables
        """
        tables = []
        
        # Check if PyMuPDF is available
        if not PYMUPDF_AVAILABLE or fitz is None:
            return tables
        
        try:
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract tables using PyMuPDF
                tables_on_page = page.find_tables()
                
                if tables_on_page and hasattr(tables_on_page, 'tables'):
                    for i, table in enumerate(tables_on_page.tables):
                        rows = []
                        
                        # Extract headers
                        headers = []
                        if table.header:
                            for cell in table.header.cells:
                                text = cell.text.strip()
                                headers.append(text)
                        
                        # Extract rows
                        for row in table.rows:
                            row_data = []
                            for cell in row.cells:
                                text = cell.text.strip()
                                row_data.append(text)
                            rows.append(row_data)
                        
                        # Create structured table representation
                        table_data = {
                            'page': page_num + 1,
                            'index_on_page': i,
                            'headers': headers,
                            'rows': rows,
                            'column_count': len(headers) if headers else (len(rows[0]) if rows else 0),
                            'row_count': len(rows)
                        }
                        
                        # Try to determine the table topic
                        topic = self._determine_table_topic(headers, rows)
                        if topic:
                            table_data['topic'] = topic
                        
                        tables.append(table_data)
            
            # Normalize table data
            for table in tables:
                self._normalize_table_data(table)
        
        except Exception as e:
            self.logger.error(f"Error extracting tables: {str(e)}")
        
        return tables
    
    def _determine_table_topic(self, headers: List[str], rows: List[List[str]]) -> str:
        """
        Determine the topic of a table based on its headers and content
        
        Args:
            headers: Table headers
            rows: Table rows
            
        Returns:
            Topic of the table or empty string if undetermined
        """
        # Join all headers
        headers_text = ' '.join(headers).lower()
        
        # Check for common sustainability topics
        if any(term in headers_text for term in ['emission', 'carbon', 'ghg', 'co2']):
            return 'emissions'
        elif any(term in headers_text for term in ['energy', 'electricity', 'fuel', 'consumption']):
            return 'energy'
        elif any(term in headers_text for term in ['water', 'effluent']):
            return 'water'
        elif any(term in headers_text for term in ['waste', 'recycling', 'landfill']):
            return 'waste'
        elif any(term in headers_text for term in ['diversity', 'employee', 'gender', 'workforce']):
            return 'social'
        elif any(term in headers_text for term in ['governance', 'board', 'management', 'compliance']):
            return 'governance'
        
        return ""
    
    def _normalize_table_data(self, table: Dict[str, Any]) -> None:
        """
        Normalize data in a table for standardized analysis
        
        Args:
            table: Table data
            
        Effects:
            Updates the table dictionary with normalized data
        """
        if 'topic' not in table or not table.get('rows'):
            return
        
        topic = table['topic']
        normalized_data = []
        
        # Determine which columns might contain values based on headers
        value_columns = []
        unit_columns = []
        metric_columns = []
        
        for i, header in enumerate(table.get('headers', [])):
            header_lower = header.lower()
            
            if any(term in header_lower for term in ['value', 'amount', 'quantity', 'total']):
                value_columns.append(i)
            elif any(term in header_lower for term in ['unit', 'measure']):
                unit_columns.append(i)
            elif any(term in header_lower for term in ['metric', 'indicator', 'parameter']):
                metric_columns.append(i)
        
        # Process rows to extract metrics and values
        for row in table['rows']:
            if not row:
                continue
            
            metric_name = ""
            value = ""
            unit = ""
            
            # Extract metric name
            if metric_columns:
                metric_name = row[metric_columns[0]]
            elif len(row) > 0:
                # Assume first column is metric name
                metric_name = row[0]
            
            # Extract value
            if value_columns:
                value = row[value_columns[0]]
            elif len(row) > 1:
                # Assume second column is value
                value = row[1]
            
            # Extract unit
            if unit_columns:
                unit = row[unit_columns[0]]
            elif len(row) > 2:
                # Assume third column might be unit
                unit = row[2]
            
            if metric_name and value:
                # Try to extract numeric value
                numeric_value = None
                numeric_match = re.search(r'\d+(?:\.\d+)?', value)
                if numeric_match:
                    try:
                        numeric_value = float(numeric_match.group(0))
                    except ValueError:
                        pass
                
                normalized_data.append({
                    'metric': metric_name,
                    'value': value,
                    'unit': unit,
                    'numeric_value': numeric_value
                })
        
        # Add normalized data to table
        table['normalized_data'] = normalized_data
    
    def _assess_framework_compliance(self, text: str, framework_id: str, 
                                   document_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess compliance with a specific regulatory framework
        
        Args:
            text: Document text
            framework_id: Framework ID
            document_structure: Document structure
            
        Returns:
            Compliance assessment
        """
        if self.base_processor and hasattr(self.base_processor, '_assess_regulatory_compliance'):
            # Use base processor's assessment as a starting point
            base_assessment = self.base_processor._assess_regulatory_compliance(text)
            
            # Extract the assessment for this framework
            if framework_id in base_assessment:
                return self._enhance_compliance_assessment(base_assessment[framework_id], text, document_structure)
        
        # Fall back to AI-based assessment if available
        if AI_CONNECTOR_AVAILABLE and is_openai_available():
            return self._assess_compliance_with_ai(text, framework_id, document_structure)
        
        # Basic assessment
        return {
            'framework_id': framework_id,
            'overall_score': 0.5,  # Default score
            'category_scores': {},
            'findings': {
                'strengths': [],
                'gaps': [],
                'recommendations': []
            },
            'recommendations': {},
            'evidence_links': {}
        }
    
    def _enhance_compliance_assessment(self, base_assessment: Dict[str, Any], 
                                     text: str, 
                                     document_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a basic compliance assessment with evidence links and more detail
        
        Args:
            base_assessment: Base compliance assessment
            text: Document text
            document_structure: Document structure
            
        Returns:
            Enhanced compliance assessment
        """
        enhanced = dict(base_assessment)  # Copy the base assessment
        
        # Add evidence links
        evidence_links = {}
        
        # Process gaps to find evidence
        for gap in enhanced.get('findings', {}).get('gaps', []):
            gap_pattern = re.escape(gap[:50])  # Use first 50 chars as a search pattern
            match = re.search(gap_pattern, text)
            
            if match:
                position = match.start()
                page = self._find_page_reference(text, position)
                
                evidence_links[gap] = {
                    'position': position,
                    'page': page,
                    'type': 'gap'
                }
        
        # Process strengths to find evidence
        for strength in enhanced.get('findings', {}).get('strengths', []):
            strength_pattern = re.escape(strength[:50])  # Use first 50 chars as a search pattern
            match = re.search(strength_pattern, text)
            
            if match:
                position = match.start()
                page = self._find_page_reference(text, position)
                
                evidence_links[strength] = {
                    'position': position,
                    'page': page,
                    'type': 'strength'
                }
        
        enhanced['evidence_links'] = evidence_links
        return enhanced
    
    def _assess_compliance_with_ai(self, text: str, framework_id: str, 
                                 document_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess compliance with a framework using AI
        
        Args:
            text: Document text
            framework_id: Framework ID
            document_structure: Document structure
            
        Returns:
            AI-based compliance assessment
        """
        if not AI_CONNECTOR_AVAILABLE or not is_openai_available():
            return {
                'framework_id': framework_id,
                'overall_score': 0.5,
                'category_scores': {},
                'findings': {
                    'strengths': [],
                    'gaps': []
                },
                'recommendations': {},
                'evidence_links': {}
            }
        
        try:
            # Prepare a prompt for OpenAI
            framework_name = {
                'esrs': 'European Sustainability Reporting Standards (ESRS)',
                'csrd': 'Corporate Sustainability Reporting Directive (CSRD)',
                'gri': 'Global Reporting Initiative (GRI)',
                'tcfd': 'Task Force on Climate-related Financial Disclosures (TCFD)',
                'sfdr': 'Sustainable Finance Disclosure Regulation (SFDR)',
                'sdg': 'Sustainable Development Goals (SDG)',
                'sasb': 'Sustainability Accounting Standards Board (SASB)'
            }.get(framework_id, framework_id.upper())
            
            prompt = f"""
            Assess compliance of the following document with the {framework_name} framework.
            
            For your assessment:
            1. Provide an overall compliance score (0-1)
            2. Identify key strengths in the document's compliance
            3. Identify gaps or areas for improvement
            4. Provide specific recommendations for enhancing compliance
            
            Return the result as a JSON object with the following structure:
            {{
                "overall_score": 0.75,
                "category_scores": {{
                    "category1": 0.8,
                    "category2": 0.7
                }},
                "findings": {{
                    "strengths": ["strength1", "strength2"],
                    "gaps": ["gap1", "gap2"]
                }},
                "recommendations": {{
                    "recommendation1": "details",
                    "recommendation2": "details"
                }}
            }}
            
            Document text:
            {text[:10000]}  # Use first 10k chars to stay within token limits
            """
            
            response = query_openai(prompt)
            
            if response and response.get('content'):
                # Parse the JSON response
                try:
                    assessment_json = json.loads(response['content'])
                    
                    # Add framework ID
                    assessment_json['framework_id'] = framework_id
                    
                    # Add empty evidence links to be filled later
                    assessment_json['evidence_links'] = {}
                    
                    return assessment_json
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse AI assessment response as JSON")
            
            # Fall back to default assessment
            return {
                'framework_id': framework_id,
                'overall_score': 0.5,
                'category_scores': {},
                'findings': {
                    'strengths': [],
                    'gaps': []
                },
                'recommendations': {},
                'evidence_links': {}
            }
        except Exception as e:
            self.logger.error(f"Error assessing compliance with AI: {str(e)}")
            return {
                'framework_id': framework_id,
                'overall_score': 0.5,
                'category_scores': {},
                'findings': {
                    'strengths': [],
                    'gaps': []
                },
                'recommendations': {},
                'evidence_links': {}
            }
    
    def _calculate_confidence_scores(self, text: str, metrics: Dict[str, List[Dict[str, Any]]], 
                                   regulatory_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate confidence scores for extracted data
        
        Args:
            text: Document text
            metrics: Extracted metrics
            regulatory_mapping: Regulatory mapping
            
        Returns:
            Confidence scores
        """
        confidence_scores = {
            'overall': 0.0,
            'metrics': {},
            'frameworks': {},
            'extraction_quality': 0.0
        }
        
        # Calculate metrics confidence
        metrics_confidence = 0.0
        metrics_count = 0
        
        for category, metrics_list in metrics.items():
            category_confidence = 0.0
            
            for metric in metrics_list:
                metric_confidence = metric.get('confidence', 0.5)
                category_confidence += metric_confidence
                metrics_count += 1
            
            if metrics_list:
                category_confidence /= len(metrics_list)
                confidence_scores['metrics'][category] = category_confidence
                metrics_confidence += category_confidence
        
        if metrics_confidence and len(metrics) > 0:
            metrics_confidence /= len(metrics)
            confidence_scores['metrics']['average'] = metrics_confidence
        
        # Calculate frameworks confidence
        frameworks_confidence = 0.0
        
        for framework, mapping in regulatory_mapping.items():
            framework_confidence = mapping.get('confidence', 0.5)
            confidence_scores['frameworks'][framework] = framework_confidence
            frameworks_confidence += framework_confidence
        
        if frameworks_confidence and len(regulatory_mapping) > 0:
            frameworks_confidence /= len(regulatory_mapping)
            confidence_scores['frameworks']['average'] = frameworks_confidence
        
        # Calculate extraction quality
        extraction_quality = 0.7  # Base extraction quality
        
        # Adjust based on text length and content
        words = text.split()
        if len(words) < 100:
            extraction_quality -= 0.2  # Very short document
        elif len(words) > 10000:
            extraction_quality += 0.1  # Rich content
        
        # Adjust based on metrics extracted
        if metrics_count > 20:
            extraction_quality += 0.1  # Many metrics found
        elif metrics_count < 5:
            extraction_quality -= 0.1  # Few metrics found
        
        # Adjust based on framework mapping
        if len(regulatory_mapping) > 1:
            extraction_quality += 0.1  # Multiple frameworks detected
        
        confidence_scores['extraction_quality'] = min(1.0, max(0.0, extraction_quality))
        
        # Calculate overall confidence
        confidence_scores['overall'] = (
            metrics_confidence * 0.4 +
            frameworks_confidence * 0.3 +
            extraction_quality * 0.3
        )
        
        return confidence_scores
    
    def _convert_to_standardized_metrics(self, metrics: Dict[str, List[Dict[str, Any]]], 
                                       document_id: int) -> List[Dict[str, Any]]:
        """
        Convert normalized metrics to standardized format for database storage
        
        Args:
            metrics: Normalized metrics
            document_id: Document ID
            
        Returns:
            List of standardized metrics
        """
        standardized_metrics = []
        
        for category, metrics_list in metrics.items():
            for metric in metrics_list:
                # Create standardized metric
                standardized_metric = {
                    'name': metric.get('match', ''),
                    'category': category,
                    'value': metric.get('value', ''),
                    'normalized_value': metric.get('normalized_value'),
                    'unit': metric.get('unit', ''),
                    'confidence': metric.get('confidence', 0.5),
                    'context': metric.get('context', ''),
                    'page': metric.get('page', 0),
                    'frameworks': {},
                    'year': metric.get('year', '')
                }
                
                # Add to standardized metrics
                standardized_metrics.append(standardized_metric)
        
        return standardized_metrics
    
    def _create_and_store_embeddings(self, text: str, document_id: int, metadata: Dict[str, Any]) -> bool:
        """
        Create vector embeddings and store them in Pinecone
        
        Args:
            text: Document text
            document_id: Document ID
            metadata: Document metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not AI_CONNECTOR_AVAILABLE or not is_pinecone_available():
            return False
        
        try:
            # Create chunks for embedding
            chunks = []
            
            # Use base processor's chunking if available
            if self.base_processor and hasattr(self.base_processor, 'chunk_document'):
                chunks = self.base_processor.chunk_document(text)
            else:
                # Simple chunking
                chunk_size = 1000
                overlap = 200
                
                words = text.split()
                for i in range(0, len(words), chunk_size - overlap):
                    chunk = ' '.join(words[i:i + chunk_size])
                    chunks.append(chunk)
            
            # Generate embeddings for each chunk
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}-{i}"
                
                # Create chunk metadata
                chunk_metadata = dict(metadata)
                chunk_metadata['chunk_id'] = i
                chunk_metadata['chunk_count'] = len(chunks)
                chunk_metadata['document_id'] = document_id
                
                # Generate embedding
                embedding = generate_embeddings(chunk)
                if embedding:
                    # Store in Pinecone
                    success = store_embeddings_in_pinecone(
                        chunk_id, 
                        embedding, 
                        chunk_metadata
                    )
                    
                    if not success:
                        self.logger.warning(f"Failed to store embedding for chunk {i}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error creating and storing embeddings: {str(e)}")
            return False

# Create a singleton instance
enhanced_processor = EnhancedDocumentProcessor()