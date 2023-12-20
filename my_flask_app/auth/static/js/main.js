//  Filename: main.js - Directory: my_flask_app/auth/static/js
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