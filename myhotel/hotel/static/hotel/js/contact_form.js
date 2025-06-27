// Contact Form Handling
    const contactForm = document.getElementById('contactForm');
    const contactFeedback = document.getElementById('contact-feedback');

    if (contactForm && contactFeedback) {
        contactForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const submitButton = contactForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            contactFeedback.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Sending...</span></div></div>';

            const formData = new FormData(contactForm);
            fetch(window.contactSubmitUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => {
                console.log("Contact response:", response.status);
                return response.json();
            })
            .then(data => {
                contactFeedback.innerHTML = '';
                if (data.success) {
                    contactFeedback.innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
                    contactForm.reset();
                } else {
                    const errorList = document.createElement('div');
                    errorList.className = 'alert alert-danger';
                    const ul = document.createElement('ul');
                    data.errors.forEach(error => {
                        const li = document.createElement('li');
                        li.textContent = error;
                        ul.appendChild(li);
                    });
                    errorList.appendChild(ul);
                    contactFeedback.appendChild(errorList);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                contactFeedback.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
            })
            .finally(() => {
                submitButton.disabled = false;
            });
        });
    }
