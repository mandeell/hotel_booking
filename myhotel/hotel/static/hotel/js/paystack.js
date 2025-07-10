document.addEventListener('DOMContentLoaded', function () {
    // Load the latest version of Paystack with modern API
    const script = document.createElement('script');
    script.src = 'https://js.paystack.co/v2/inline.js';
    script.async = true;
    script.onload = () => {
        console.log('Paystack SDK v2 loaded successfully');
        console.log('PaystackPop available:', typeof PaystackPop !== 'undefined');
        
        if (typeof PaystackPop !== 'undefined') {
            console.log('PaystackPop constructor:', typeof PaystackPop);
            console.log('PaystackPop methods:', Object.getOwnPropertyNames(PaystackPop.prototype || {}));
        }
        
        // Dispatch a custom event when Paystack is ready
        window.dispatchEvent(new CustomEvent('paystackReady'));
    };
    script.onerror = () => {
        console.error('Failed to load Paystack SDK v2, trying v1...');
        // Fallback to v1
        const fallbackScript = document.createElement('script');
        fallbackScript.src = 'https://js.paystack.co/v1/inline.js';
        fallbackScript.async = true;
        fallbackScript.onload = () => {
            console.log('Paystack SDK v1 loaded successfully (fallback)');
            console.log('PaystackPop available:', typeof PaystackPop !== 'undefined');
            if (typeof PaystackPop !== 'undefined') {
                console.log('PaystackPop.setup:', typeof PaystackPop.setup);
            }
            // Dispatch a custom event when Paystack is ready
            window.dispatchEvent(new CustomEvent('paystackReady'));
        };
        fallbackScript.onerror = () => {
            console.error('Failed to load Paystack SDK v1 as well');
            // Dispatch event anyway so the app doesn't hang
            window.dispatchEvent(new CustomEvent('paystackReady'));
        };
        document.head.appendChild(fallbackScript);
    };
    document.head.appendChild(script);
});