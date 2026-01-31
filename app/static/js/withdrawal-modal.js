    // Open Modal
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    // Close Modal
    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal.id);
            }
        }
    });

    // Update currency icon
    function updateWithdrawIcon(select) {
        const option = select.options[select.selectedIndex];
        const iconClass = option.getAttribute('data-icon');
        const iconElement = select.parentElement.querySelector('.select-icon');
        iconElement.className = `fas ${iconClass} select-icon`;
    }

    // Handle form submission
    document.getElementById('withdrawForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const currency = document.getElementById('withdrawCurrency').value;
        const amount = document.getElementById('withdrawAmount').value;
        const walletAddress = document.getElementById('walletAddress').value;
        const confirmAddress = document.getElementById('confirmWalletAddress').value;

        // Validation
        if (!amount || parseFloat(amount.replace('$', '')) <= 0) {
            alert('Please enter a valid amount');
            return;
        }

        if (!walletAddress) {
            alert('Please enter a wallet address');
            return;
        }

        if (walletAddress !== confirmAddress) {
            alert('Wallet addresses do not match');
            return;
        }

        // Submit to backend
        console.log('Withdrawal request:', { currency, amount, walletAddress });

        // Close modal and show success message
        closeModal('withdrawModal');
        alert('Withdrawal request submitted successfully!');

        // Reset form
        this.reset();
    });