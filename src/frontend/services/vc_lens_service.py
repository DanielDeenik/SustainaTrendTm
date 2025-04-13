"""
VC Lens Service

Handles document processing, vector storage, and analysis for the VC Lens module.
Implements RAG (Retrieval-Augmented Generation), MCP (Multi-Context Processing), and OCR (Optical Character Recognition).
"""

import os
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import base64
import io
import re
import numpy as np
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)

class VCLensService:
    """Service for VC Lens document processing and analysis"""
    
    def __init__(self):
        """Initialize VC Lens service"""
        # Initialize vector store
        self.vector_store = {}
        self.document_store = {}
        self.metadata_store = {}
        
        # Initialize TF-IDF vectorizer for text similarity
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Load existing documents if available
        self._load_documents()
        
        logger.info("VC Lens Service initialized")
    
    def process_document(self, document_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a document using OCR, extract text, and store its vector representation
        
        Args:
            document_path: Path to the document file
            metadata: Optional metadata about the document
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Generate unique ID for the document
            doc_id = str(uuid.uuid4())
            
            # Extract text based on file type
            file_ext = os.path.splitext(document_path)[1].lower()
            
            if file_ext in ['.pdf']:
                text = self._extract_text_from_pdf(document_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                text = self._extract_text_from_image(document_path)
            else:
                # For text files, read directly
                with open(document_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Extract entities and key information
            entities = self._extract_entities(text)
            
            # Chunk text for processing
            chunks = self._chunk_text(text)
            
            # Store document metadata
            doc_metadata = {
                'doc_id': doc_id,
                'filename': os.path.basename(document_path),
                'processed_at': datetime.now().isoformat(),
                'chunk_count': len(chunks),
                'file_type': file_ext,
                'entities': entities,
                **(metadata or {})
            }
            
            # Store document and metadata
            self.document_store[doc_id] = {
                'text': text,
                'chunks': chunks,
                'entities': entities
            }
            self.metadata_store[doc_id] = doc_metadata
            
            # Generate and store vectors
            self._generate_vectors(doc_id, chunks)
            
            # Save documents
            self._save_documents()
            
            return {
                'success': True,
                'doc_id': doc_id,
                'chunks_processed': len(chunks),
                'entities': entities
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_similar(self, query: str, limit: int = 5, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            filter_criteria: Optional criteria to filter results
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not self.vector_store:
                return []
            
            # Generate query vector
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            results = []
            for doc_id, doc_vectors in self.vector_store.items():
                # Skip if doesn't match filter criteria
                if filter_criteria and not self._matches_filter(doc_id, filter_criteria):
                    continue
                
                # Calculate max similarity across all chunks
                max_similarity = 0
                best_chunk_idx = 0
                
                for i, chunk_vector in enumerate(doc_vectors):
                    similarity = cosine_similarity(query_vector, chunk_vector)[0][0]
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_chunk_idx = i
                
                # Add to results if similarity is above threshold
                if max_similarity > 0.1:
                    doc_data = self.document_store[doc_id]
                    results.append({
                        'doc_id': doc_id,
                        'score': float(max_similarity),
                        'chunk_index': best_chunk_idx,
                        'text': doc_data['chunks'][best_chunk_idx],
                        'metadata': self.metadata_store[doc_id],
                        'entities': doc_data['entities']
                    })
            
            # Sort by score and limit results
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []
    
    def analyze_startup(self, doc_id: str, analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Analyze a startup document using RAG and MCP
        
        Args:
            doc_id: Document ID to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        try:
            if doc_id not in self.document_store:
                return {'success': False, 'error': 'Document not found'}
            
            doc_data = self.document_store[doc_id]
            metadata = self.metadata_store[doc_id]
            
            # Perform different types of analysis
            if analysis_type == 'comprehensive':
                # Extract key information
                company_info = self._extract_company_info(doc_data['text'])
                
                # Analyze market opportunity
                market_analysis = self._analyze_market(doc_data['text'])
                
                # Analyze team
                team_analysis = self._analyze_team(doc_data['text'])
                
                # Analyze financials
                financial_analysis = self._analyze_financials(doc_data['text'])
                
                # Analyze sustainability metrics
                sustainability_analysis = self._analyze_sustainability(doc_data['text'])
                
                # Generate investment recommendation
                recommendation = self._generate_recommendation(
                    company_info, 
                    market_analysis, 
                    team_analysis, 
                    financial_analysis,
                    sustainability_analysis
                )
                
                return {
                    'success': True,
                    'company_info': company_info,
                    'market_analysis': market_analysis,
                    'team_analysis': team_analysis,
                    'financial_analysis': financial_analysis,
                    'sustainability_analysis': sustainability_analysis,
                    'recommendation': recommendation
                }
            
            elif analysis_type == 'sustainability':
                # Focus only on sustainability analysis
                sustainability_analysis = self._analyze_sustainability(doc_data['text'])
                
                return {
                    'success': True,
                    'sustainability_analysis': sustainability_analysis
                }
            
            else:
                return {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}
            
        except Exception as e:
            logger.error(f"Error analyzing startup: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def compare_portfolio_fit(self, doc_id: str, portfolio_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare a startup document against portfolio investment criteria
        
        Args:
            doc_id: Document ID to analyze
            portfolio_criteria: Portfolio investment criteria
            
        Returns:
            Portfolio fit analysis
        """
        try:
            if doc_id not in self.document_store:
                return {'success': False, 'error': 'Document not found'}
            
            doc_data = self.document_store[doc_id]
            
            # Extract company information
            company_info = self._extract_company_info(doc_data['text'])
            
            # Calculate fit scores for different criteria
            fit_scores = {}
            
            # Market fit
            if 'market_criteria' in portfolio_criteria:
                market_fit = self._calculate_market_fit(
                    doc_data['text'], 
                    portfolio_criteria['market_criteria']
                )
                fit_scores['market_fit'] = market_fit
            
            # Team fit
            if 'team_criteria' in portfolio_criteria:
                team_fit = self._calculate_team_fit(
                    doc_data['text'], 
                    portfolio_criteria['team_criteria']
                )
                fit_scores['team_fit'] = team_fit
            
            # Financial fit
            if 'financial_criteria' in portfolio_criteria:
                financial_fit = self._calculate_financial_fit(
                    doc_data['text'], 
                    portfolio_criteria['financial_criteria']
                )
                fit_scores['financial_fit'] = financial_fit
            
            # Sustainability fit
            if 'sustainability_criteria' in portfolio_criteria:
                sustainability_fit = self._calculate_sustainability_fit(
                    doc_data['text'], 
                    portfolio_criteria['sustainability_criteria']
                )
                fit_scores['sustainability_fit'] = sustainability_fit
            
            # Calculate overall fit score
            if fit_scores:
                overall_fit = sum(fit_scores.values()) / len(fit_scores)
            else:
                overall_fit = 0
            
            return {
                'success': True,
                'company_info': company_info,
                'fit_scores': fit_scores,
                'overall_fit': overall_fit,
                'recommendation': self._generate_fit_recommendation(overall_fit, fit_scores)
            }
            
        except Exception as e:
            logger.error(f"Error comparing portfolio fit: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using regex patterns"""
        entities = {
            'company_names': [],
            'people': [],
            'locations': [],
            'dates': [],
            'numbers': [],
            'urls': []
        }
        
        # Extract company names (capitalized words)
        company_pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b'
        entities['company_names'] = re.findall(company_pattern, text)
        
        # Extract people (Mr., Mrs., Dr., etc.)
        people_pattern = r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b'
        entities['people'] = re.findall(people_pattern, text)
        
        # Extract locations (cities, countries)
        location_pattern = r'\b(?:New York|London|Paris|Tokyo|Berlin|Beijing|Mumbai|Sydney|Toronto|San Francisco)\b'
        entities['locations'] = re.findall(location_pattern, text)
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        entities['dates'] = re.findall(date_pattern, text)
        
        # Extract numbers (including currency)
        number_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d+)?\b'
        entities['numbers'] = re.findall(number_pattern, text)
        
        # Extract URLs
        url_pattern = r'https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?'
        entities['urls'] = re.findall(url_pattern, text)
        
        return entities
    
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for processing"""
        # Simple chunking by size
        chunks = []
        current_chunk = ""
        
        for paragraph in text.split('\n\n'):
            if len(current_chunk) + len(paragraph) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _generate_vectors(self, doc_id: str, chunks: List[str]) -> None:
        """Generate and store vectors for document chunks"""
        try:
            # Fit vectorizer if not already fitted
            if not hasattr(self.vectorizer, 'vocabulary_') or not self.vectorizer.vocabulary_:
                self.vectorizer.fit(chunks)
            
            # Transform chunks to vectors
            vectors = self.vectorizer.transform(chunks).toarray()
            
            # Store vectors
            self.vector_store[doc_id] = vectors
            
        except Exception as e:
            logger.error(f"Error generating vectors: {str(e)}")
    
    def _matches_filter(self, doc_id: str, filter_criteria: Dict[str, Any]) -> bool:
        """Check if document matches filter criteria"""
        if doc_id not in self.metadata_store:
            return False
        
        metadata = self.metadata_store[doc_id]
        
        for key, value in filter_criteria.items():
            if key not in metadata or metadata[key] != value:
                return False
        
        return True
    
    def _extract_company_info(self, text: str) -> Dict[str, Any]:
        """Extract company information from text"""
        company_info = {
            'name': '',
            'description': '',
            'founded_year': '',
            'headquarters': '',
            'website': '',
            'industry': '',
            'stage': ''
        }
        
        # Extract company name (first capitalized entity)
        company_names = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', text)
        if company_names:
            company_info['name'] = company_names[0]
        
        # Extract website
        urls = re.findall(r'https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?', text)
        if urls:
            company_info['website'] = urls[0]
        
        # Extract founded year
        year_pattern = r'(?:founded|established|incorporated) (?:in )?(\d{4})'
        year_match = re.search(year_pattern, text, re.IGNORECASE)
        if year_match:
            company_info['founded_year'] = year_match.group(1)
        
        # Extract headquarters
        location_pattern = r'(?:headquarters|based|located) (?:in )?([A-Z][a-zA-Z]+(?:,\s*[A-Z][a-zA-Z]+)*)'
        location_match = re.search(location_pattern, text, re.IGNORECASE)
        if location_match:
            company_info['headquarters'] = location_match.group(1)
        
        # Extract industry
        industry_pattern = r'(?:industry|sector):\s*([A-Za-z\s&]+)'
        industry_match = re.search(industry_pattern, text, re.IGNORECASE)
        if industry_match:
            company_info['industry'] = industry_match.group(1).strip()
        
        # Extract stage
        stage_pattern = r'(?:stage|funding round):\s*([A-Za-z\s]+)'
        stage_match = re.search(stage_pattern, text, re.IGNORECASE)
        if stage_match:
            company_info['stage'] = stage_match.group(1).strip()
        
        # Extract description (first paragraph)
        paragraphs = text.split('\n\n')
        if paragraphs:
            company_info['description'] = paragraphs[0]
        
        return company_info
    
    def _analyze_market(self, text: str) -> Dict[str, Any]:
        """Analyze market opportunity from text"""
        market_analysis = {
            'market_size': '',
            'growth_rate': '',
            'competitors': [],
            'competitive_advantage': '',
            'market_trends': []
        }
        
        # Extract market size
        size_pattern = r'(?:market size|TAM|SAM|SOM):\s*\$?(\d+(?:\.\d+)?(?:B|M|K|billion|million|thousand))'
        size_match = re.search(size_pattern, text, re.IGNORECASE)
        if size_match:
            market_analysis['market_size'] = size_match.group(1)
        
        # Extract growth rate
        growth_pattern = r'(?:growth rate|CAGR):\s*(\d+(?:\.\d+)?%)'
        growth_match = re.search(growth_pattern, text, re.IGNORECASE)
        if growth_match:
            market_analysis['growth_rate'] = growth_match.group(1)
        
        # Extract competitors
        competitor_pattern = r'(?:competitors|competition):\s*([A-Za-z\s,]+)'
        competitor_match = re.search(competitor_pattern, text, re.IGNORECASE)
        if competitor_match:
            competitors = competitor_match.group(1).split(',')
            market_analysis['competitors'] = [c.strip() for c in competitors]
        
        # Extract competitive advantage
        advantage_pattern = r'(?:competitive advantage|differentiator):\s*([A-Za-z\s,]+)'
        advantage_match = re.search(advantage_pattern, text, re.IGNORECASE)
        if advantage_match:
            market_analysis['competitive_advantage'] = advantage_match.group(1).strip()
        
        # Extract market trends
        trend_pattern = r'(?:market trends|industry trends):\s*([A-Za-z\s,]+)'
        trend_match = re.search(trend_pattern, text, re.IGNORECASE)
        if trend_match:
            trends = trend_match.group(1).split(',')
            market_analysis['market_trends'] = [t.strip() for t in trends]
        
        return market_analysis
    
    def _analyze_team(self, text: str) -> Dict[str, Any]:
        """Analyze team from text"""
        team_analysis = {
            'founders': [],
            'key_members': [],
            'experience': '',
            'expertise': []
        }
        
        # Extract founders
        founder_pattern = r'(?:founders|founded by):\s*([A-Za-z\s,]+)'
        founder_match = re.search(founder_pattern, text, re.IGNORECASE)
        if founder_match:
            founders = founder_match.group(1).split(',')
            team_analysis['founders'] = [f.strip() for f in founders]
        
        # Extract key members
        member_pattern = r'(?:key members|team members|leadership):\s*([A-Za-z\s,]+)'
        member_match = re.search(member_pattern, text, re.IGNORECASE)
        if member_match:
            members = member_match.group(1).split(',')
            team_analysis['key_members'] = [m.strip() for m in members]
        
        # Extract experience
        experience_pattern = r'(?:experience|background):\s*([A-Za-z\s,]+)'
        experience_match = re.search(experience_pattern, text, re.IGNORECASE)
        if experience_match:
            team_analysis['experience'] = experience_match.group(1).strip()
        
        # Extract expertise
        expertise_pattern = r'(?:expertise|skills):\s*([A-Za-z\s,]+)'
        expertise_match = re.search(expertise_pattern, text, re.IGNORECASE)
        if expertise_match:
            expertise = expertise_match.group(1).split(',')
            team_analysis['expertise'] = [e.strip() for e in expertise]
        
        return team_analysis
    
    def _analyze_financials(self, text: str) -> Dict[str, Any]:
        """Analyze financials from text"""
        financial_analysis = {
            'revenue': '',
            'growth_rate': '',
            'funding': '',
            'burn_rate': '',
            'unit_economics': {}
        }
        
        # Extract revenue
        revenue_pattern = r'(?:revenue|ARR|MRR):\s*\$?(\d+(?:\.\d+)?(?:B|M|K|billion|million|thousand))'
        revenue_match = re.search(revenue_pattern, text, re.IGNORECASE)
        if revenue_match:
            financial_analysis['revenue'] = revenue_match.group(1)
        
        # Extract growth rate
        growth_pattern = r'(?:growth rate|YoY growth):\s*(\d+(?:\.\d+)?%)'
        growth_match = re.search(growth_pattern, text, re.IGNORECASE)
        if growth_match:
            financial_analysis['growth_rate'] = growth_match.group(1)
        
        # Extract funding
        funding_pattern = r'(?:funding|raised|investment):\s*\$?(\d+(?:\.\d+)?(?:B|M|K|billion|million|thousand))'
        funding_match = re.search(funding_pattern, text, re.IGNORECASE)
        if funding_match:
            financial_analysis['funding'] = funding_match.group(1)
        
        # Extract burn rate
        burn_pattern = r'(?:burn rate|cash burn):\s*\$?(\d+(?:\.\d+)?(?:B|M|K|billion|million|thousand))'
        burn_match = re.search(burn_pattern, text, re.IGNORECASE)
        if burn_match:
            financial_analysis['burn_rate'] = burn_match.group(1)
        
        # Extract unit economics
        unit_pattern = r'(?:unit economics|CAC|LTV):\s*([A-Za-z\s,]+)'
        unit_match = re.search(unit_pattern, text, re.IGNORECASE)
        if unit_match:
            unit_info = unit_match.group(1).strip()
            financial_analysis['unit_economics'] = {'description': unit_info}
        
        return financial_analysis
    
    def _analyze_sustainability(self, text: str) -> Dict[str, Any]:
        """Analyze sustainability metrics from text"""
        sustainability_analysis = {
            'carbon_footprint': '',
            'energy_usage': '',
            'water_usage': '',
            'waste_management': '',
            'sustainability_goals': [],
            'esg_score': ''
        }
        
        # Extract carbon footprint
        carbon_pattern = r'(?:carbon footprint|emissions|CO2):\s*(\d+(?:\.\d+)?(?:tons|tonnes|t|kg|g))'
        carbon_match = re.search(carbon_pattern, text, re.IGNORECASE)
        if carbon_match:
            sustainability_analysis['carbon_footprint'] = carbon_match.group(1)
        
        # Extract energy usage
        energy_pattern = r'(?:energy usage|power consumption):\s*(\d+(?:\.\d+)?(?:kWh|MWh|GWh))'
        energy_match = re.search(energy_pattern, text, re.IGNORECASE)
        if energy_match:
            sustainability_analysis['energy_usage'] = energy_match.group(1)
        
        # Extract water usage
        water_pattern = r'(?:water usage|water consumption):\s*(\d+(?:\.\d+)?(?:L|m³|gallons))'
        water_match = re.search(water_pattern, text, re.IGNORECASE)
        if water_match:
            sustainability_analysis['water_usage'] = water_match.group(1)
        
        # Extract waste management
        waste_pattern = r'(?:waste management|recycling rate):\s*(\d+(?:\.\d+)?%)'
        waste_match = re.search(waste_pattern, text, re.IGNORECASE)
        if waste_match:
            sustainability_analysis['waste_management'] = waste_match.group(1)
        
        # Extract sustainability goals
        goals_pattern = r'(?:sustainability goals|environmental goals):\s*([A-Za-z\s,]+)'
        goals_match = re.search(goals_pattern, text, re.IGNORECASE)
        if goals_match:
            goals = goals_match.group(1).split(',')
            sustainability_analysis['sustainability_goals'] = [g.strip() for g in goals]
        
        # Extract ESG score
        esg_pattern = r'(?:ESG score|sustainability rating):\s*(\d+(?:\.\d+)?)'
        esg_match = re.search(esg_pattern, text, re.IGNORECASE)
        if esg_match:
            sustainability_analysis['esg_score'] = esg_match.group(1)
        
        return sustainability_analysis
    
    def _generate_recommendation(self, company_info, market_analysis, team_analysis, financial_analysis, sustainability_analysis):
        """Generate investment recommendation based on analysis"""
        # Simple recommendation logic
        recommendation = {
            'decision': 'Consider',
            'confidence': 'Medium',
            'key_factors': [],
            'risks': [],
            'next_steps': []
        }
        
        # Evaluate market
        if market_analysis.get('market_size') and market_analysis.get('growth_rate'):
            recommendation['key_factors'].append(f"Market size: {market_analysis['market_size']} with {market_analysis['growth_rate']} growth")
        else:
            recommendation['risks'].append("Limited market information")
        
        # Evaluate team
        if team_analysis.get('founders') and team_analysis.get('experience'):
            recommendation['key_factors'].append(f"Experienced founders: {', '.join(team_analysis['founders'])}")
        else:
            recommendation['risks'].append("Limited team information")
        
        # Evaluate financials
        if financial_analysis.get('revenue') and financial_analysis.get('growth_rate'):
            recommendation['key_factors'].append(f"Revenue: {financial_analysis['revenue']} with {financial_analysis['growth_rate']} growth")
        else:
            recommendation['risks'].append("Limited financial information")
        
        # Evaluate sustainability
        if sustainability_analysis.get('esg_score'):
            recommendation['key_factors'].append(f"ESG Score: {sustainability_analysis['esg_score']}")
        else:
            recommendation['risks'].append("Limited sustainability information")
        
        # Set recommendation based on factors
        if len(recommendation['key_factors']) >= 3 and len(recommendation['risks']) <= 1:
            recommendation['decision'] = 'Strong Consider'
            recommendation['confidence'] = 'High'
        elif len(recommendation['key_factors']) >= 2 and len(recommendation['risks']) <= 2:
            recommendation['decision'] = 'Consider'
            recommendation['confidence'] = 'Medium'
        else:
            recommendation['decision'] = 'Pass'
            recommendation['confidence'] = 'Low'
        
        # Set next steps
        if recommendation['decision'] != 'Pass':
            recommendation['next_steps'].append("Schedule a call with the founders")
            recommendation['next_steps'].append("Request detailed financial projections")
            recommendation['next_steps'].append("Conduct technical due diligence")
        
        return recommendation
    
    def _calculate_market_fit(self, text: str, criteria: Dict[str, Any]) -> float:
        """Calculate market fit score"""
        # Simple implementation - in a real system, this would use more sophisticated NLP
        score = 0.5  # Default score
        
        # Check if text contains keywords from criteria
        if 'keywords' in criteria:
            for keyword in criteria['keywords']:
                if keyword.lower() in text.lower():
                    score += 0.1
        
        # Check if text contains industry from criteria
        if 'industry' in criteria and criteria['industry'].lower() in text.lower():
            score += 0.2
        
        # Check if text contains market size from criteria
        if 'min_market_size' in criteria:
            size_pattern = r'\$(\d+(?:\.\d+)?(?:B|M|K|billion|million|thousand))'
            size_matches = re.findall(size_pattern, text, re.IGNORECASE)
            if size_matches:
                # Simple comparison - in a real system, this would parse the values
                score += 0.2
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _calculate_team_fit(self, text: str, criteria: Dict[str, Any]) -> float:
        """Calculate team fit score"""
        # Simple implementation
        score = 0.5  # Default score
        
        # Check if text contains keywords from criteria
        if 'keywords' in criteria:
            for keyword in criteria['keywords']:
                if keyword.lower() in text.lower():
                    score += 0.1
        
        # Check if text contains experience from criteria
        if 'experience' in criteria and criteria['experience'].lower() in text.lower():
            score += 0.2
        
        # Check if text contains expertise from criteria
        if 'expertise' in criteria:
            for skill in criteria['expertise']:
                if skill.lower() in text.lower():
                    score += 0.1
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _calculate_financial_fit(self, text: str, criteria: Dict[str, Any]) -> float:
        """Calculate financial fit score"""
        # Simple implementation
        score = 0.5  # Default score
        
        # Check if text contains keywords from criteria
        if 'keywords' in criteria:
            for keyword in criteria['keywords']:
                if keyword.lower() in text.lower():
                    score += 0.1
        
        # Check if text contains revenue from criteria
        if 'min_revenue' in criteria:
            revenue_pattern = r'\$(\d+(?:\.\d+)?(?:B|M|K|billion|million|thousand))'
            revenue_matches = re.findall(revenue_pattern, text, re.IGNORECASE)
            if revenue_matches:
                # Simple comparison - in a real system, this would parse the values
                score += 0.2
        
        # Check if text contains growth rate from criteria
        if 'min_growth' in criteria:
            growth_pattern = r'(\d+(?:\.\d+)?%)'
            growth_matches = re.findall(growth_pattern, text, re.IGNORECASE)
            if growth_matches:
                # Simple comparison - in a real system, this would parse the values
                score += 0.2
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _calculate_sustainability_fit(self, text: str, criteria: Dict[str, Any]) -> float:
        """Calculate sustainability fit score"""
        # Simple implementation
        score = 0.5  # Default score
        
        # Check if text contains keywords from criteria
        if 'keywords' in criteria:
            for keyword in criteria['keywords']:
                if keyword.lower() in text.lower():
                    score += 0.1
        
        # Check if text contains ESG score from criteria
        if 'min_esg_score' in criteria:
            esg_pattern = r'ESG score:?\s*(\d+(?:\.\d+)?)'
            esg_match = re.search(esg_pattern, text, re.IGNORECASE)
            if esg_match:
                # Simple comparison - in a real system, this would parse the values
                score += 0.2
        
        # Check if text contains sustainability goals from criteria
        if 'sustainability_goals' in criteria:
            for goal in criteria['sustainability_goals']:
                if goal.lower() in text.lower():
                    score += 0.1
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _generate_fit_recommendation(self, overall_fit: float, fit_scores: Dict[str, float]) -> str:
        """Generate recommendation based on fit scores"""
        if overall_fit >= 0.8:
            return "Strong fit with portfolio criteria. Recommended for investment."
        elif overall_fit >= 0.6:
            return "Good fit with portfolio criteria. Consider for investment with some due diligence."
        elif overall_fit >= 0.4:
            return "Moderate fit with portfolio criteria. Further evaluation needed."
        else:
            return "Limited fit with portfolio criteria. Not recommended for investment at this time."
    
    def _load_documents(self) -> None:
        """Load documents from storage"""
        try:
            # In a real implementation, this would load from a database
            # For now, we'll use a simple file-based storage
            storage_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vc_lens')
            os.makedirs(storage_path, exist_ok=True)
            
            # Load document store
            doc_store_path = os.path.join(storage_path, 'document_store.json')
            if os.path.exists(doc_store_path):
                with open(doc_store_path, 'r') as f:
                    self.document_store = json.load(f)
            
            # Load metadata store
            metadata_store_path = os.path.join(storage_path, 'metadata_store.json')
            if os.path.exists(metadata_store_path):
                with open(metadata_store_path, 'r') as f:
                    self.metadata_store = json.load(f)
            
            # Load vector store
            vector_store_path = os.path.join(storage_path, 'vector_store.json')
            if os.path.exists(vector_store_path):
                with open(vector_store_path, 'r') as f:
                    # Convert lists back to numpy arrays
                    vector_data = json.load(f)
                    self.vector_store = {k: np.array(v) for k, v in vector_data.items()}
            
            logger.info(f"Loaded {len(self.document_store)} documents from storage")
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
    
    def _save_documents(self) -> None:
        """Save documents to storage"""
        try:
            # In a real implementation, this would save to a database
            # For now, we'll use a simple file-based storage
            storage_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vc_lens')
            os.makedirs(storage_path, exist_ok=True)
            
            # Save document store
            doc_store_path = os.path.join(storage_path, 'document_store.json')
            with open(doc_store_path, 'w') as f:
                json.dump(self.document_store, f)
            
            # Save metadata store
            metadata_store_path = os.path.join(storage_path, 'metadata_store.json')
            with open(metadata_store_path, 'w') as f:
                json.dump(self.metadata_store, f)
            
            # Save vector store
            vector_store_path = os.path.join(storage_path, 'vector_store.json')
            with open(vector_store_path, 'w') as f:
                # Convert numpy arrays to lists for JSON serialization
                vector_data = {k: v.tolist() for k, v in self.vector_store.items()}
                json.dump(vector_data, f)
            
            logger.info(f"Saved {len(self.document_store)} documents to storage")
            
        except Exception as e:
            logger.error(f"Error saving documents: {str(e)}") 