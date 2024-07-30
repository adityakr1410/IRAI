document.addEventListener('DOMContentLoaded', function() {
    restrictDateSelection();
});

function restrictDateSelection() {
    const dateInput = document.getElementById('date-selector');
    const today = new Date();
    const maxDate = new Date();
    maxDate.setDate(today.getDate() - 5);
    
    const maxDateString = maxDate.toISOString().split('T')[0];
    dateInput.setAttribute('max', today.toISOString().split('T')[0]);
    dateInput.setAttribute('min', maxDateString);
}

function checkAmount() {
    const amountInput = document.getElementById('amount-input').value;
    const amount = parseInt(amountInput, 10);
    
    if (amount < 1000) {
        alert('Minimum amount to pay is 1000');
    }
}
