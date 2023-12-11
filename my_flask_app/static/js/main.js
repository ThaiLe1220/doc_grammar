//  Filename: main.js - Directory: my_flask_app/static/js
window.addEventListener('DOMContentLoaded', (event) => {
  // Select all elements with class 'flash-message' (or the class you use for flash messages)
  const flashMessages = document.querySelectorAll('.flash-message');

	// Scroll to the corrections section if it exists
	const correctionsSection = document.getElementById('corrections');
	if (correctionsSection) {
		correctionsSection.scrollIntoView({ behavior: 'smooth' });
	}

  // Set timeout to remove each message after 3 seconds
  flashMessages.forEach(message => {
      setTimeout(() => {
          message.remove();
      }, 5000); // 5 seconds
  }); 
});


function fetchCorrections(fileId) {
  fetch(`/corrections/${fileId}`)
    .then(response => response.json())
    .then(corrections => {
      // Clear previous corrections
      const correctionsContainer = document.getElementById('corrections');
      correctionsContainer.innerHTML = ''; // Clear out any existing corrections
      
      // Create HTML for each correction and append it to the container
      corrections.forEach(correction => {
        const correctionDetail = document.createElement('div');
        correctionDetail.className = 'correction-detail';
        
        correctionDetail.innerHTML = `
          <p><strong>Original Text:</strong> ${correction.original_sentence}</p>
          <p><strong>Corrected Text:</strong> ${correction.corrected_sentence}</p>
          <p><strong>Modified Text:</strong> [${correction.modified_tokens.join(', ')}]</p>
          <p><strong>Added Text:</strong> [${correction.added_tokens.join(', ')}]</p>
        `;
        
        correctionsContainer.appendChild(correctionDetail);
      });

      // Scroll to corrections
      if (correctionsContainer) {
        correctionsContainer.scrollIntoView({ behavior: 'smooth' });
      }
    })
    .catch(error => console.error('Error fetching corrections:', error));
}
