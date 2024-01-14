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

// Stripe subscription functionality
var stripe = Stripe('pk_test_51OReIZCS2kdynUVumJcWQAWQ1xsXuApU3cNWwVBc88D1rSFN7uI5EQErxTk54XsP8mypOQFSfkQR4oj6DwivLdpo00pRdYPqjE');
var subscribeButton = document.getElementById('subscribe-button');
if (subscribeButton) {
  subscribeButton.addEventListener('click', function () {
    console.log('Subscribe button clicked'); // This should appear in your console
    console.log('Fetching:', window.location.origin + '/subscribe');
    fetch('/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin'
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (session) {
        return stripe.redirectToCheckout({ sessionId: session.id });
      })
      .then(function (result) {
        if (result.error) {
          alert(result.error.message);
        }
      })
      .catch(function (error) {
        console.error('Error:', error);
      });
  });
}

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

// Stripe subscription functionality
var stripe = Stripe('pk_test_51OVEkqDAl3fqs0z5WYJHtSc1Jn2WZD4w7vV7rVOULeHvdgYSoXxa415eCxTnYBZ0xTXCqDBdW5xla4hw1xyjumQQ00T45kDMNP');
var subscribeButton = document.getElementById('subscribe-button');
if (subscribeButton) {
  subscribeButton.addEventListener('click', function () {
    console.log('Subscribe button clicked'); // This should appear in your console
    console.log('Fetching:', window.location.origin + '/subscribe');
    fetch('/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin'
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (session) {
        return stripe.redirectToCheckout({ sessionId: session.id });
      })
      .then(function (result) {
        if (result.error) {
          alert(result.error.message);
        }
      })
      .catch(function (error) {
        console.error('Error:', error);
      });
  });
}