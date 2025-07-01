document.addEventListener('DOMContentLoaded', function () {
    const script = document.createElement('script');
    script.src = 'https://js.paystack.co/v1/inline.js';
    script.async = true;
    script.onload = () => console.log('Paystack SDK loaded successfully');
    script.onerror = () => console.error('Failed to load Paystack SDK');
    document.head.appendChild(script);
});