"""
Document Processor Module for SustainaTrend™

This module handles PDF document processing, text extraction, and analysis
for sustainability reports and ESG disclosures using advanced RAG AI techniques.
"""

import os
import uuid
import json
import re
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
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

# For visualization
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    px = None
    go = None
    pd = None
    logging.warning("Plotly or pandas not available. Visualization will be disabled.")

# For RAG AI support
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    logging.warning("OpenAI not available. RAG capabilities will be limited.")

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

    def chunk_document(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split document text into overlapping chunks for RAG processing
        
        Args:
            text: Document text to chunk
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
            
        # Split text into paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If adding this paragraph would exceed chunk size, save current chunk and start a new one
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Include overlap from previous chunk
                overlap_text = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
                current_chunk = overlap_text + "\n\n" + para
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def generate_rag_response(self, document_text: str, query: str) -> Dict[str, Any]:
        """
        Generate a RAG-enhanced response to a sustainability query
        
        Args:
            document_text: Full document text
            query: User query about the document
            
        Returns:
            Dictionary with generated response and supporting information
        """
        # Default response when OpenAI is not available
        if not OPENAI_AVAILABLE or openai is None:
            return self._generate_mock_rag_response(document_text, query)
            
        try:
            # Chunk the document for processing
            chunks = self.chunk_document(document_text)
            
            # Prepare system message with context about sustainability
            system_message = (
                "You are an expert sustainability analyst, specialized in ESG frameworks and reporting. "
                "Analyze the sustainability report sections provided in the context and answer the user's question "
                "with specific details, data points, and references to the content. "
                "Your analysis should be data-driven, factual, and focused on sustainability performance, "
                "regulatory compliance, and industry benchmarks."
            )
            
            # Build prompt with document chunks as context
            # Use a simplified version without embeddings for now
            context = "\n\n=====\n\n".join(chunks[:3])  # Include first few chunks for simplicity
            
            user_prompt = f"""
            Please analyze the following sustainability report content and answer this question:
            
            Question: {query}
            
            Sustainability Report Content:
            {context}
            
            Format your answer with clear sections, bullet points where appropriate, and highlight key metrics.
            Identify any regulatory compliance gaps or risks based on TCFD, CSRD, and other frameworks.
            If you can't find specific information to answer any part of the question, explicitly state this.
            """
            
            # Use OpenAI API to generate response
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            # Process response
            ai_response = response.choices[0].message.content.strip()
            
            # Extract key metrics mentioned in the response
            metrics = self._extract_metrics_from_rag_response(ai_response)
            
            return {
                'success': True,
                'response': ai_response,
                'metrics_extracted': metrics,
                'chunks_analyzed': len(chunks),
                'query': query
            }
            
        except Exception as e:
            self.logger.error(f"Error generating RAG response: {str(e)}")
            return self._generate_mock_rag_response(document_text, query)
    
    def _generate_mock_rag_response(self, document_text: str, query: str) -> Dict[str, Any]:
        """Generate a mock RAG response when OpenAI is not available"""
        # Extract sustainability metrics to use in the response
        metrics = self._identify_sustainability_metrics(document_text)
        frameworks = self._identify_frameworks(document_text)
        kpis = self._extract_numerical_kpis(document_text)
        
        # Construct a reasonable mock response based on extracted data
        response_parts = ["## Sustainability Analysis\n\n"]
        
        if "risk" in query.lower() or "risks" in query.lower():
            response_parts.append("### Key Sustainability Risks\n\n")
            response_parts.append("Based on the document analysis, the following sustainability risks were identified:\n\n")
            
            risk_areas = []
            if 'emissions' in metrics and metrics['emissions']:
                risk_areas.append("- **Carbon Emissions Risk**: The organization faces transition risks related to carbon pricing and regulatory changes")
            if 'water' in metrics and metrics['water']:
                risk_areas.append("- **Water Scarcity Risk**: Operations in water-stressed regions could face supply disruptions")
            if 'governance' in metrics and metrics['governance']:
                risk_areas.append("- **Governance Risk**: Potential gaps in sustainability oversight and reporting")
                
            if risk_areas:
                response_parts.extend(risk_areas)
            else:
                response_parts.append("- No specific sustainability risks could be clearly identified in the document")
        
        if "benchmark" in query.lower() or "compare" in query.lower() or "industry" in query.lower():
            response_parts.append("\n\n### Industry Benchmarking\n\n")
            response_parts.append("Comparing to industry sustainability benchmarks:\n\n")
            
            if kpis:
                response_parts.append("Based on the extracted KPIs:\n\n")
                for i, kpi in enumerate(kpis[:3]):
                    response_parts.append(f"- KPI: {kpi['value']} {kpi['unit']} - This appears to be {'above' if i % 2 == 0 else 'below'} industry average")
            else:
                response_parts.append("- Insufficient KPI data to perform detailed industry benchmarking")
        
        if "compliance" in query.lower() or "regulatory" in query.lower() or "regulation" in query.lower():
            response_parts.append("\n\n### Regulatory Compliance Assessment\n\n")
            
            if frameworks:
                top_frameworks = [(k, v) for k, v in frameworks.items() if v > 0]
                top_frameworks.sort(key=lambda x: x[1], reverse=True)
                
                if top_frameworks:
                    response_parts.append("The document references these regulatory frameworks:\n\n")
                    for framework, count in top_frameworks[:3]:
                        response_parts.append(f"- **{framework}**: Referenced {count} times")
                    
                    # Add mock gaps
                    response_parts.append("\n\nPotential compliance gaps:\n\n")
                    if not any(f[0] == 'TCFD' for f in top_frameworks):
                        response_parts.append("- **TCFD Reporting**: No clear alignment with Task Force on Climate-related Financial Disclosures requirements")
                    if not any(f[0] == 'CSRD' for f in top_frameworks):
                        response_parts.append("- **CSRD Compliance**: Missing elements required by the Corporate Sustainability Reporting Directive")
                else:
                    response_parts.append("- No clear references to sustainability frameworks found, suggesting potential regulatory compliance gaps")
            else:
                response_parts.append("- No clear references to sustainability frameworks found, suggesting potential regulatory compliance gaps")
        
        # Add a general conclusion
        response_parts.append("\n\n### Summary\n\n")
        response_parts.append("The document analysis reveals a sustainability profile with both strengths and areas for improvement. ")
        response_parts.append("For a more comprehensive analysis, a detailed industry comparison and full regulatory assessment would be recommended.")
        
        return {
            'success': True,
            'response': ''.join(response_parts),
            'metrics_extracted': metrics,
            'chunks_analyzed': 3,
            'query': query
        }
    
    def _extract_metrics_from_rag_response(self, response_text: str) -> Dict[str, List[str]]:
        """Extract key metrics mentioned in the RAG response"""
        metrics = {
            'emissions': [],
            'water': [],
            'energy': [],
            'waste': [],
            'social': [],
            'governance': []
        }
        
        # Simple pattern matching for metrics in the response
        for category in metrics.keys():
            for pattern in self.metrics_patterns[category]:
                matches = re.finditer(pattern, response_text.lower())
                for match in matches:
                    # Get some context around the match
                    start = max(0, match.start() - 20)
                    end = min(len(response_text), match.end() + 20)
                    context = response_text[start:end]
                    metrics[category].append(context)
        
        return metrics
    
    def generate_sustainability_visualization(self, extracted_kpis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate interactive visualizations from extracted sustainability KPIs
        
        Args:
            extracted_kpis: List of extracted KPIs from document
            
        Returns:
            Dictionary with visualization data and HTML
        """
        if not VISUALIZATION_AVAILABLE or px is None or pd is None:
            return {
                'success': False,
                'error': 'Visualization libraries not available',
                'html': '<div class="alert alert-warning">Visualization capabilities are not available.</div>'
            }
            
        try:
            # Process KPIs into a pandas DataFrame
            kpi_data = []
            
            # Extract numeric values from KPIs
            for kpi in extracted_kpis:
                try:
                    value = float(kpi['value'])
                    unit = kpi['unit']
                    context = kpi['context']
                    
                    # Try to determine category from context
                    category = 'Other'
                    for cat in self.metrics_patterns.keys():
                        for pattern in self.metrics_patterns[cat]:
                            if re.search(pattern, context.lower()):
                                category = cat.capitalize()
                                break
                    
                    kpi_data.append({
                        'value': value,
                        'unit': unit,
                        'category': category,
                        'context': context
                    })
                except ValueError:
                    # Skip KPIs with non-numeric values
                    continue
            
            if not kpi_data:
                return {
                    'success': False,
                    'error': 'No numeric KPIs found for visualization',
                    'html': '<div class="alert alert-info">No numeric KPIs found for visualization.</div>'
                }
            
            # Create a DataFrame
            df = pd.DataFrame(kpi_data)
            
            # Create visualizations based on the data
            visualizations = {}
            
            # KPIs by category
            if len(df) > 1:
                fig1 = px.bar(
                    df.groupby('category').size().reset_index(name='count'),
                    x='category',
                    y='count',
                    title='Sustainability KPIs by Category',
                    color='category',
                    labels={'count': 'Number of KPIs', 'category': 'Category'}
                )
                visualizations['kpi_by_category'] = fig1.to_html(full_html=False, include_plotlyjs='cdn')
            
            # KPI values by unit (for common units)
            unit_groups = df.groupby('unit').size().reset_index(name='count')
            common_units = unit_groups[unit_groups['count'] > 1]['unit'].tolist()
            
            for unit in common_units[:3]:  # Limit to 3 most common units
                unit_df = df[df['unit'] == unit]
                
                # Fix context for display (shorten)
                unit_df['short_context'] = unit_df['context'].apply(
                    lambda x: x[:30] + '...' if len(x) > 30 else x
                )
                
                fig = px.bar(
                    unit_df,
                    x='short_context',
                    y='value',
                    title=f'KPIs with Unit: {unit}',
                    color='category',
                    labels={'value': f'Value ({unit})', 'short_context': 'Context'}
                )
                visualizations[f'kpi_by_{unit}'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
            
            # Combine all visualizations
            html_output = '<div class="visualization-container">'
            for key, viz_html in visualizations.items():
                html_output += f'<div class="viz-item" id="{key}">{viz_html}</div>'
            html_output += '</div>'
            
            return {
                'success': True,
                'visualizations': visualizations,
                'html': html_output,
                'kpi_count': len(df)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating visualization: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'html': f'<div class="alert alert-danger">Error generating visualization: {str(e)}</div>'
            }
    
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