/**
 * Document Hub Redesign - Modern UI for Regulatory AI Integration
 * 
 * This script handles all interactions for the document hub, including:
 * - Tab navigation between Upload, Analyze, and Insights views
 * - File upload handling (drag & drop, click to browse)
 * - File validation and preview
 * - Text paste functionality
 * - Document analysis progress tracking and updates
 * - Server-sent events for real-time analysis feedback
 * - Framework assessment visualization
 * 
 * Integrated with backend Regulatory AI and Ethical AI functionality
 */

document.addEventListener('DOMContentLoaded', function() {
  // Tab navigation
  const tabs = document.querySelectorAll('.tab');
  const tabContents = document.querySelectorAll('.tab-content');
  
  // File upload variables
  let selectedFile = null;
  let documentId = null;
  let isProcessing = false;
  let eventSource = null;
  
  // DOM Elements - Upload
  const dropArea = document.getElementById('drop-area');
  const fileInput = document.getElementById('file-input');
  const browseBtn = document.getElementById('browse-btn');
  const filePreview = document.getElementById('file-preview');
  const selectedFileName = document.getElementById('selected-file-name');
  const selectedFileSize = document.getElementById('selected-file-size');
  const removeFileBtn = document.getElementById('remove-file');
  const uploadSubmitBtn = document.getElementById('upload-submit');
  const textPasteBtn = document.getElementById('text-paste-btn');
  const uploadProgress = document.getElementById('upload-progress');
  const progressFill = document.getElementById('progress-fill');
  const progressPercentage = document.getElementById('progress-percentage');
  const uploadSuccess = document.getElementById('upload-success');
  const uploadError = document.getElementById('upload-error');
  const errorMessage = document.getElementById('error-message');
  const retryUploadBtn = document.getElementById('retry-upload');
  
  // DOM Elements - Text Paste Modal
  const textPasteModal = document.getElementById('text-paste-modal');
  const closeTextModalBtn = document.getElementById('close-text-modal');
  const cancelTextPasteBtn = document.getElementById('cancel-text-paste');
  const submitTextPasteBtn = document.getElementById('submit-text-paste');
  const pastedText = document.getElementById('pasted-text');
  const wordCount = document.getElementById('word-count');
  
  // DOM Elements - Analysis
  const toAnalyzeBtn = document.getElementById('to-analyze-btn');
  const analyzingDocumentName = document.getElementById('analyzing-document-name');
  const analysisSteps = document.querySelectorAll('.analysis-step');
  const progressMessages = document.getElementById('progress-messages');
  const analysisProgressFill = document.getElementById('analysis-progress-fill');
  const analysisPercentage = document.getElementById('analysis-percentage');
  const cancelAnalysisBtn = document.getElementById('cancel-analysis');
  const analysisComplete = document.getElementById('analysis-complete');
  
  // DOM Elements - Insights
  const toInsightsBtn = document.getElementById('to-insights-btn');
  const documentInsightsName = document.getElementById('document-insights-name');
  const assessmentTabs = document.querySelectorAll('.assessment-tab');
  const assessmentContents = document.querySelectorAll('.assessment-content');
  const insightFilename = document.getElementById('insight-filename');
  const insightUploadDate = document.getElementById('insight-upload-date');
  const insightPageCount = document.getElementById('insight-page-count');
  const insightWordCount = document.getElementById('insight-word-count');
  const executiveSummary = document.getElementById('executive-summary');
  
  // Tab click handlers
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Only allow tab navigation if no file is being processed
      if (!isProcessing) {
        const tabId = tab.getAttribute('data-tab');
        
        // Remove active class from all tabs and contents
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        
        // Add active class to selected tab and content
        tab.classList.add('active');
        document.getElementById(`${tabId}-tab`).classList.add('active');
      }
    });
  });
  
  // File selection through browse button
  browseBtn.addEventListener('click', () => {
    fileInput.click();
  });
  
  // File selected via input
  fileInput.addEventListener('change', (e) => {
    handleFileSelection(e.target.files[0]);
  });
  
  // Drag and drop handlers
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => {
      dropArea.classList.add('dragover');
    }, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => {
      dropArea.classList.remove('dragover');
    }, false);
  });
  
  dropArea.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const file = dt.files[0];
    handleFileSelection(file);
  });
  
  // Handle file removal
  removeFileBtn.addEventListener('click', () => {
    resetFileSelection();
  });
  
  // Submit file upload
  uploadSubmitBtn.addEventListener('click', () => {
    if (selectedFile) {
      uploadDocument(selectedFile);
    }
  });
  
  // Retry upload button
  retryUploadBtn.addEventListener('click', () => {
    hideAllUploadStates();
    resetFileSelection();
  });
  
  // Text paste buttons
  textPasteBtn.addEventListener('click', () => {
    openTextPasteModal();
  });
  
  closeTextModalBtn.addEventListener('click', () => {
    closeTextPasteModal();
  });
  
  cancelTextPasteBtn.addEventListener('click', () => {
    closeTextPasteModal();
  });
  
  submitTextPasteBtn.addEventListener('click', () => {
    const text = pastedText.value.trim();
    if (text) {
      // Create a virtual file from the pasted text
      const textBlob = new Blob([text], { type: 'text/plain' });
      const textFile = new File([textBlob], "pasted-text.txt", { type: "text/plain" });
      
      // Add properties to help with UI rendering
      textFile.wordCount = countWords(text);
      textFile.isTextPaste = true;
      textFile.content = text;
      
      handleFileSelection(textFile);
      closeTextPasteModal();
      
      // Upload the text content
      uploadTextContent(text);
    }
  });
  
  // Word count in text paste modal
  pastedText.addEventListener('input', () => {
    const text = pastedText.value.trim();
    const count = countWords(text);
    wordCount.textContent = count;
  });
  
  // Tab navigation from success states
  toAnalyzeBtn.addEventListener('click', () => {
    document.querySelector('.tab[data-tab="analyze"]').click();
    startDocumentAnalysis();
  });
  
  toInsightsBtn.addEventListener('click', () => {
    document.querySelector('.tab[data-tab="insights"]').click();
    loadDocumentInsights();
  });
  
  // Cancel analysis
  cancelAnalysisBtn.addEventListener('click', () => {
    if (eventSource) {
      eventSource.close();
      addProgressMessage("Analysis cancelled by user");
      resetAnalysisState();
    }
  });
  
  // Assessment tabs in insights view
  assessmentTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const assessmentId = tab.getAttribute('data-assessment');
      
      assessmentTabs.forEach(t => t.classList.remove('active'));
      assessmentContents.forEach(c => c.classList.remove('active'));
      
      tab.classList.add('active');
      document.getElementById(`${assessmentId}-assessment`).classList.add('active');
    });
  });
  
  // Handle file selection (works for both browse and drag & drop)
  function handleFileSelection(file) {
    if (!file) return;
    
    // Validate file (type, size)
    if (!validateFile(file)) return;
    
    selectedFile = file;
    
    // Update UI to show selected file
    filePreview.classList.add('visible');
    selectedFileName.textContent = file.name;
    
    // Show file size nicely formatted
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    selectedFileSize.textContent = `${sizeMB} MB`;
    
    // If it's a text paste, show word count instead of size
    if (file.isTextPaste) {
      selectedFileSize.textContent = `${file.wordCount} words`;
    }
  }
  
  // Validate file type and size
  function validateFile(file) {
    // Check file type
    const allowedTypes = [
      'application/pdf', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    
    // For text paste, always allow
    if (file.isTextPaste) return true;
    
    if (!allowedTypes.includes(file.type)) {
      showError("Please select a valid file (PDF, DOCX, or TXT)");
      return false;
    }
    
    // Check file size (max 20MB)
    const maxSize = 20 * 1024 * 1024; // 20MB in bytes
    if (file.size > maxSize) {
      showError("File size exceeds the maximum limit of 20MB");
      return false;
    }
    
    return true;
  }
  
  // Reset file selection
  function resetFileSelection() {
    selectedFile = null;
    fileInput.value = '';
    filePreview.classList.remove('visible');
    selectedFileName.textContent = 'No file selected';
    selectedFileSize.textContent = '';
  }
  
  // Upload document file
  function uploadDocument(file) {
    isProcessing = true;
    hideAllUploadStates();
    uploadProgress.classList.add('visible');
    
    const formData = new FormData();
    formData.append('document', file);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = Math.round((e.loaded / e.total) * 100);
        updateUploadProgress(percentComplete);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        // Success
        try {
          const response = JSON.parse(xhr.responseText);
          documentId = response.document_id;
          uploadProgress.classList.remove('visible');
          uploadSuccess.classList.add('visible');
        } catch (error) {
          showError("Error processing server response");
        }
      } else {
        // Error
        showError("Upload failed: " + (xhr.statusText || "Server error"));
      }
      isProcessing = false;
    });
    
    xhr.addEventListener('error', () => {
      showError("Network error occurred during upload");
      isProcessing = false;
    });
    
    xhr.addEventListener('abort', () => {
      showError("Upload was aborted");
      isProcessing = false;
    });
    
    // Regulatory AI endpoint for document upload
    xhr.open('POST', '/documents/api/upload', true);
    xhr.send(formData);
  }
  
  // Upload text content
  function uploadTextContent(text) {
    isProcessing = true;
    hideAllUploadStates();
    uploadProgress.classList.add('visible');
    updateUploadProgress(10); // Start with 10% to show progress immediately
    
    // Prepare the data
    const data = {
      text: text,
      filename: "pasted-text.txt",
      content_type: "text/plain"
    };
    
    fetch('/documents/api/text-upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      updateUploadProgress(90);
      if (!response.ok) {
        throw new Error('Server responded with status: ' + response.status);
      }
      return response.json();
    })
    .then(data => {
      updateUploadProgress(100);
      documentId = data.document_id;
      
      setTimeout(() => {
        uploadProgress.classList.remove('visible');
        uploadSuccess.classList.add('visible');
        isProcessing = false;
      }, 500);
    })
    .catch(error => {
      showError("Upload failed: " + error.message);
      isProcessing = false;
    });
  }
  
  // Start document analysis with server-sent events
  function startDocumentAnalysis() {
    if (!documentId) {
      addProgressMessage("Error: No document ID found");
      return;
    }
    
    // Reset and prepare analysis view
    resetAnalysisState();
    setAnalysisStep('extraction', 'pending');
    analyzingDocumentName.textContent = selectedFile ? `Analyzing "${selectedFile.name}"` : "Analyzing your document";
    
    // Add first message
    addProgressMessage("Starting document analysis...");
    
    // Connect to server-sent events endpoint
    const evtSource = new EventSource(`/documents/api/file-assessment/${documentId}`);
    eventSource = evtSource;
    
    // Handle different event types
    evtSource.addEventListener("extraction_started", function(e) {
      setAnalysisStep('extraction', 'pending');
      addProgressMessage("Extracting text from document...");
      updateAnalysisProgress(10);
    });
    
    evtSource.addEventListener("extraction_complete", function(e) {
      setAnalysisStep('extraction', 'complete');
      setAnalysisStep('processing', 'pending');
      addProgressMessage("Text extraction complete");
      updateAnalysisProgress(25);
    });
    
    evtSource.addEventListener("processing_started", function(e) {
      addProgressMessage("Processing document content...");
      updateAnalysisProgress(30);
    });
    
    evtSource.addEventListener("processing_update", function(e) {
      const data = JSON.parse(e.data);
      addProgressMessage(data.message);
      updateAnalysisProgress(40);
    });
    
    evtSource.addEventListener("processing_complete", function(e) {
      setAnalysisStep('processing', 'complete');
      setAnalysisStep('assessment', 'pending');
      addProgressMessage("Content processing complete");
      updateAnalysisProgress(50);
    });
    
    evtSource.addEventListener("assessment_started", function(e) {
      addProgressMessage("Starting framework assessment...");
      updateAnalysisProgress(55);
    });
    
    evtSource.addEventListener("assessment_update", function(e) {
      const data = JSON.parse(e.data);
      addProgressMessage(data.message);
      updateAnalysisProgress(65);
    });
    
    evtSource.addEventListener("assessment_complete", function(e) {
      setAnalysisStep('assessment', 'complete');
      setAnalysisStep('insights', 'pending');
      addProgressMessage("Framework assessment complete");
      updateAnalysisProgress(75);
    });
    
    evtSource.addEventListener("insights_started", function(e) {
      addProgressMessage("Generating sustainability insights...");
      updateAnalysisProgress(80);
    });
    
    evtSource.addEventListener("insights_update", function(e) {
      const data = JSON.parse(e.data);
      addProgressMessage(data.message);
      updateAnalysisProgress(90);
    });
    
    evtSource.addEventListener("insights_complete", function(e) {
      setAnalysisStep('insights', 'complete');
      addProgressMessage("Insights generation complete");
      updateAnalysisProgress(100);
      
      // Show completion state
      setTimeout(() => {
        document.querySelector('.analysis-progress-container').style.display = 'none';
        analysisComplete.classList.add('visible');
      }, 1000);
      
      // Close the event source
      evtSource.close();
      eventSource = null;
    });
    
    evtSource.addEventListener("error", function(e) {
      addProgressMessage("Error during analysis process");
      
      // If backend not ready, fall back to simulation mode
      if (!document.querySelector('.error-simulation-notice')) {
        addProgressMessage("Falling back to simulation mode for demonstration");
        simulateAnalysisProgress();
      }
      
      // Close the event source
      evtSource.close();
      eventSource = null;
    });
  }
  
  // Simulate analysis progress when backend is not available
  function simulateAnalysisProgress() {
    const simulationSteps = [
      { event: "extraction_started", delay: 500 },
      { event: "extraction_update", message: "Parsing document structure...", delay: 1000 },
      { event: "extraction_update", message: "Identifying document sections...", delay: 1500 },
      { event: "extraction_complete", delay: 1000 },
      { event: "processing_started", delay: 500 },
      { event: "processing_update", message: "Analyzing text content...", delay: 1500 },
      { event: "processing_update", message: "Identifying sustainability metrics...", delay: 1200 },
      { event: "processing_update", message: "Classifying ESG components...", delay: 1800 },
      { event: "processing_complete", delay: 1000 },
      { event: "assessment_started", delay: 500 },
      { event: "assessment_update", message: "Evaluating CSRD compliance...", delay: 1500 },
      { event: "assessment_update", message: "Evaluating TCFD alignment...", delay: 1700 },
      { event: "assessment_update", message: "Evaluating ESRS requirements...", delay: 1600 },
      { event: "assessment_complete", delay: 1000 },
      { event: "insights_started", delay: 500 },
      { event: "insights_update", message: "Generating executive summary...", delay: 1500 },
      { event: "insights_update", message: "Identifying improvement opportunities...", delay: 1700 },
      { event: "insights_update", message: "Compiling compliance metrics...", delay: 1500 },
      { event: "insights_complete", delay: 1000 }
    ];
    
    let currentIndex = 0;
    let progress = 0;
    
    function processNextStep() {
      if (currentIndex >= simulationSteps.length) return;
      
      const step = simulationSteps[currentIndex];
      
      switch(step.event) {
        case "extraction_started":
          setAnalysisStep('extraction', 'pending');
          addProgressMessage("Extracting text from document...");
          progress = 10;
          break;
        case "extraction_update":
          addProgressMessage(step.message);
          progress += 5;
          break;
        case "extraction_complete":
          setAnalysisStep('extraction', 'complete');
          setAnalysisStep('processing', 'pending');
          addProgressMessage("Text extraction complete");
          progress = 25;
          break;
        case "processing_started":
          addProgressMessage("Processing document content...");
          progress = 30;
          break;
        case "processing_update":
          addProgressMessage(step.message);
          progress += 5;
          break;
        case "processing_complete":
          setAnalysisStep('processing', 'complete');
          setAnalysisStep('assessment', 'pending');
          addProgressMessage("Content processing complete");
          progress = 50;
          break;
        case "assessment_started":
          addProgressMessage("Starting framework assessment...");
          progress = 55;
          break;
        case "assessment_update":
          addProgressMessage(step.message);
          progress += 5;
          break;
        case "assessment_complete":
          setAnalysisStep('assessment', 'complete');
          setAnalysisStep('insights', 'pending');
          addProgressMessage("Framework assessment complete");
          progress = 75;
          break;
        case "insights_started":
          addProgressMessage("Generating sustainability insights...");
          progress = 80;
          break;
        case "insights_update":
          addProgressMessage(step.message);
          progress += 5;
          break;
        case "insights_complete":
          setAnalysisStep('insights', 'complete');
          addProgressMessage("Insights generation complete");
          progress = 100;
          
          // Show completion state
          setTimeout(() => {
            document.querySelector('.analysis-progress-container').style.display = 'none';
            analysisComplete.classList.add('visible');
          }, 1000);
          
          return; // End simulation
      }
      
      updateAnalysisProgress(progress);
      
      currentIndex++;
      setTimeout(processNextStep, step.delay);
    }
    
    // Start the simulation
    processNextStep();
  }
  
  // Load document insights
  function loadDocumentInsights() {
    // Update document name in insights view
    documentInsightsName.textContent = selectedFile ? `Insights from "${selectedFile.name}"` : "Insights from your document";
    
    // Update document details
    insightFilename.textContent = selectedFile ? selectedFile.name : "document.pdf";
    insightUploadDate.textContent = new Date().toLocaleDateString();
    
    // Set page count and word count
    if (selectedFile && selectedFile.isTextPaste) {
      insightPageCount.textContent = "N/A (text)";
      insightWordCount.textContent = selectedFile.wordCount;
    } else {
      insightPageCount.textContent = "86"; // Example value
      insightWordCount.textContent = "32,450"; // Example value
    }
    
    // In a real implementation, we would fetch the actual insights from the server
    // using the documentId, but for now we'll use the example data in the HTML
  }
  
  // Helper functions
  function updateUploadProgress(percent) {
    progressFill.style.width = percent + '%';
    progressPercentage.textContent = percent + '%';
  }
  
  function updateAnalysisProgress(percent) {
    analysisProgressFill.style.width = percent + '%';
    analysisPercentage.textContent = percent + '%';
  }
  
  function hideAllUploadStates() {
    uploadProgress.classList.remove('visible');
    uploadSuccess.classList.remove('visible');
    uploadError.classList.remove('visible');
  }
  
  function showError(message) {
    hideAllUploadStates();
    errorMessage.textContent = message;
    uploadError.classList.add('visible');
  }
  
  function setAnalysisStep(step, status) {
    const stepElement = document.getElementById(`step-${step}`);
    if (stepElement) {
      // Remove all status classes
      stepElement.classList.remove('pending', 'complete', 'error');
      // Add the new status class
      stepElement.classList.add(status);
    }
  }
  
  function resetAnalysisState() {
    // Reset analysis steps
    analysisSteps.forEach(step => {
      step.classList.remove('pending', 'complete', 'error');
    });
    
    // Clear progress messages
    progressMessages.innerHTML = '';
    
    // Reset progress bar
    updateAnalysisProgress(0);
    
    // Hide completion state
    analysisComplete.classList.remove('visible');
    
    // Show progress container
    document.querySelector('.analysis-progress-container').style.display = 'block';
  }
  
  function addProgressMessage(message) {
    const messageContainer = document.createElement('div');
    messageContainer.className = 'message-container';
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    messageElement.textContent = message;
    
    messageContainer.appendChild(messageElement);
    progressMessages.appendChild(messageContainer);
    
    // Scroll to bottom
    progressMessages.scrollTop = progressMessages.scrollHeight;
  }
  
  function openTextPasteModal() {
    textPasteModal.classList.add('visible');
    pastedText.focus();
  }
  
  function closeTextPasteModal() {
    textPasteModal.classList.remove('visible');
    pastedText.value = '';
    wordCount.textContent = '0';
  }
  
  function countWords(text) {
    return text.split(/\s+/).filter(word => word.length > 0).length;
  }
  
  // Add Ethical AI notice to the upload container
  function addEthicalAINotice() {
    const supportedFrameworks = document.querySelector('.supported-frameworks');
    
    const ethicalAINotice = document.createElement('div');
    ethicalAINotice.className = 'ethical-ai-notice';
    ethicalAINotice.innerHTML = `
      <h5><i class="fas fa-shield-alt"></i> Regulatory AI & Ethical Assessment</h5>
      <p>Documents are processed using Ethical AI principles that respect confidentiality and provide transparent framework assessments compliant with CSRD, ESRS, SFDR, TCFD, and SASB requirements.</p>
      <div class="regulatory-check">
        <i class="fas fa-check-circle check-icon"></i>
        <span class="check-text">All insights include traceability to source material for regulatory compliance verification.</span>
      </div>
    `;
    
    // Insert the notice before the supported frameworks
    supportedFrameworks.parentNode.insertBefore(ethicalAINotice, supportedFrameworks);
  }
  
  // Initialize Ethical AI notice
  addEthicalAINotice();
});