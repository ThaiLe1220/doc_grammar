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

// Go to Billing Plan page
const billingBtn = document.querySelector('.functions .billingBtn');

billingBtn.addEventListener('click', () => {
  window.location.href = '/billing-plan';
});

function confirmLogout() {
  var result = confirm("Are you sure you want to log out?");
  if (result) {
    // location.href='{{ url_for('logout') }}';
    window.location.href = '/logout';
  } else {
    alert("Logout canceled.");
  }
}



// document.getElementById('submitButton').addEventListener('click', function(event) {
//   var button = this;
//   event.preventDefault(); // Prevent form submission for demonstration purposes
//   button.classList.add('loading'); // Add the loading class to show the spinner

//   // Simulate a 3-second loading process
//   setTimeout(function() {
//     button.classList.remove('loading'); // Remove the loading class
//     button.classList.add('success'); // Add the success class

//     var span = button.querySelector('span');
//     if (span) {
//       span.textContent = 'Success'; // Change the button text to 'Success'
//     }

//     // Optionally, remove the success state after some time
//     setTimeout(function() {
//       button.classList.remove('success');
//       span.textContent = 'Submit'; // Change the text back to 'Submit'
//     }, 2000); // Time before reverting the success message

//   }, 3000); // Time to show the spinner
// });

document.getElementById('submitButton').addEventListener('click', function(event) {
  var button = this;
  button.classList.add('loading'); // Add the loading class to show the spinner
  var spinner = button.querySelector('.spinner');
  var textWrapper = button.querySelector('.textWrapper');
  
  // Show spinner and hide text
  spinner.style.display = 'block';
  textWrapper.style.opacity = '0';
  textWrapper.style.visibility = 'hidden';
  
  // No need to prevent the default form submission
  // The form will submit and the page will reload or redirect as per the action attribute
});




function updateButtonState() {
  var checkboxes = document.querySelectorAll('input[name="file-checkbox"]');
  var atLeastOneChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

  var buttons = document.querySelectorAll('.action-buttons button');
  
  buttons.forEach(button => {
    if (atLeastOneChecked) {
      // If at least one checkbox is checked, enable the buttons
      button.classList.remove('disabled');
    } else {
      // If no checkboxes are checked, disable the buttons
      button.classList.add('disabled');
    }
  });
}

// Initial check on page load
document.addEventListener('DOMContentLoaded', updateButtonState);

// Add change event listeners to checkboxes
document.querySelectorAll('input[name="file-checkbox"]').forEach(checkbox => {
  checkbox.addEventListener('change', updateButtonState);
});
