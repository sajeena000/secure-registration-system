// frontend/static/js/app.js

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    // Page-specific initializations based on the current URL path
    if (path === '/' || path.startsWith('/login')) {
        initLoginPage();
    } else if (path.startsWith('/register')) {
        initRegisterPage();
    } else if (path.startsWith('/profile')) {
        initProfilePage();
    } else if (path.startsWith('/verify-email')) {
        initVerifyPage();
    } else if (path.startsWith('/forgot-password')) {
        initForgotPasswordPage();
    } else if (path.startsWith('/reset-password')) {
        initResetPasswordPage();
    }
});

// --- UTILITY FUNCTIONS ---
function displayMessage(elementId, message, isError = true) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.style.display = 'block';
    el.className = isError ? 'error-message' : 'success-message';
}

function hideMessage(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.style.display = 'none';
}

function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.btn-show-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const passwordInput = button.previousElementSibling;
            const icon = button.querySelector('i');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
}


// --- LOGIN PAGE ---
function initLoginPage() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    initPasswordToggles();

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('error-message');

        const formData = new FormData(loginForm);
        
        try {
            const response = await fetch('/api/v1/auth/token', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed.');
            }
            
            window.location.href = '/profile'; 

        } catch (error) {
            displayMessage('error-message', error.message);
        }
    });
}

// --- REGISTER PAGE ---
function initRegisterPage() {
    const registerForm = document.getElementById('registerForm');
    const refreshCaptchaBtn = document.getElementById('refreshCaptcha');
    
    const passwordInput = document.getElementById('password');
    const passwordConfirmInput = document.getElementById('password_confirm');
    const strengthMeter = document.getElementById('password-strength-meter');
    const confirmFeedback = document.getElementById('password-confirm-feedback');

    if (!registerForm || !passwordInput || !passwordConfirmInput || !strengthMeter || !confirmFeedback) return;

    loadCaptcha();
    initPasswordToggles();

    refreshCaptchaBtn.addEventListener('click', loadCaptcha);
    
    passwordInput.addEventListener('input', () => updatePasswordStrengthVisuals(passwordInput, strengthMeter));
    passwordInput.addEventListener('input', () => updatePasswordMatchVisuals(passwordInput, passwordConfirmInput, confirmFeedback));
    passwordConfirmInput.addEventListener('input', () => updatePasswordMatchVisuals(passwordInput, passwordConfirmInput, confirmFeedback));

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('error-message');

        const formData = new FormData(registerForm);
        const password = formData.get('password');
        const passwordConfirm = formData.get('password_confirm');

        if (password !== passwordConfirm) {
            displayMessage('error-message', 'Passwords do not match.');
            return;
        }

        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/v1/users/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Registration failed.');
            }

            const formContainer = document.querySelector('.form-container');
            formContainer.innerHTML = `
                <div class="header">
                    <h2><i class="fas fa-paper-plane" style="color: var(--success-color); margin-right: 1rem;"></i>Almost there!</h2>
                    <p>We've sent a verification link to your email address. Please check your inbox (and spam folder) to activate your account.</p>
                </div>
                <div class="footer">
                    <p><a href="/">Back to Login</a></p>
                </div>
            `;

        } catch (error) {
            displayMessage('error-message', error.message);
            loadCaptcha(); // Refresh CAPTCHA on error
        }
    });
}

async function loadCaptcha() {
    try {
        const response = await fetch('/api/v1/captcha/');
        if (!response.ok) throw new Error('Failed to load CAPTCHA.');
        const data = await response.json();
        
        document.getElementById('captchaImage').src = `data:image/png;base64,${data.image_base64}`;
        document.getElementById('captcha_id').value = data.captcha_id;
    } catch (error) {
        displayMessage('error-message', error.message);
    }
}

// --- Password Strength Visuals ---
function updatePasswordStrengthVisuals(passwordInput, strengthMeter) {
    if (!passwordInput || !strengthMeter) return;

    const password = passwordInput.value;
    const strengthBar = strengthMeter.querySelector('.strength-bar');
    const strengthText = strengthMeter.querySelector('.strength-text');

    if (!strengthBar || !strengthText) return;

    if (password.length === 0) {
        strengthBar.style.width = '0%';
        strengthText.textContent = '';
        return;
    }

    const length = password.length;
    let strength = "Very Weak"; 
    const feedbackItems = [];

    if (length < 12) {
        feedbackItems.push("must be at least 12 characters long");
    }

    const hasLowercase = /[a-z]/.test(password);
    const hasUppercase = /[A-Z]/.test(password);
    const hasDigit = /\d/.test(password);
    const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    const charTypes = [hasLowercase, hasUppercase, hasDigit, hasSymbol].filter(Boolean).length;
    
    const missingTypes = [];
    if (!hasLowercase) missingTypes.push("lowercase letters");
    if (!hasUppercase) missingTypes.push("uppercase letters");
    if (!hasDigit) missingTypes.push("numbers");
    if (!hasSymbol) missingTypes.push("symbols");

    if (missingTypes.length > 0) {
        feedbackItems.push(`should include ${missingTypes.join(', ')}`);
    }
        
    if (length >= 12 && charTypes === 4) {
        strength = (length >= 16) ? "Very Strong" : "Strong";
    } else if (length >= 12 && charTypes === 3) {
        strength = "Moderate";
    } else if (length >= 8) {
        strength = "Weak";
    } else {
        strength = "Very Weak";
    }

    let message = '';
    if (strength === "Very Strong") {
        message = "This is a very strong password.";
    } else if (strength === "Strong") {
        message = "This is a strong password. Make it 16+ characters for even better security.";
    } else {
        if (feedbackItems.length > 0) {
            const feedbackString = feedbackItems.join(', ').replace(/, ([^,]*)$/, ' and $1');
            message = `Password is ${strength.toLowerCase()}: it ${feedbackString}.`;
        } else {
             message = `Password is ${strength.toLowerCase()} and does not meet all security requirements.`;
        }
    }

    let color = "#d32f2f"; // Deep red
    let width = "15%";

    switch (strength) {
        case "Weak":
            width = "35%";
            color = "#cf6679"; // Lighter red
            break;
        case "Moderate":
            width = "60%";
            color = "#ffd54f"; // yellow
            break;
        case "Strong":
            width = "85%";
            color = "#a5d6a7"; // light green
            break;
        case "Very Strong":
            width = "100%";
            color = "#66bb6a"; // var(--success-color)
            break;
    }

    strengthBar.style.width = width;
    strengthBar.style.backgroundColor = color;
    strengthText.textContent = message;
}

// --- Password Match Visuals ---
function updatePasswordMatchVisuals(passwordInput, confirmInput, feedbackEl) {
    if (!passwordInput || !confirmInput || !feedbackEl) return;
    const password = passwordInput.value;
    const passwordConfirm = confirmInput.value;

    if (passwordConfirm.length === 0) {
        feedbackEl.textContent = '';
        feedbackEl.className = 'feedback-text';
        return;
    }

    if (password === passwordConfirm) {
        feedbackEl.textContent = '✓ Passwords match';
        feedbackEl.className = 'feedback-text match';
    } else {
        feedbackEl.textContent = '✗ Passwords do not match';
        feedbackEl.className = 'feedback-text mismatch';
    }
}

// --- VERIFY EMAIL PAGE ---
async function initVerifyPage() {
    if (typeof verificationToken === 'undefined' || !verificationToken) {
        console.error("Verification token not found.");
        return;
    }
    
    const statusIcon = document.getElementById('status-icon');
    const statusHeading = document.getElementById('status-heading');
    const statusMessage = document.getElementById('status-message');
    const actionContainer = document.getElementById('action-button-container');

    try {
        const response = await fetch(`/api/v1/users/verify-email?token=${verificationToken}`, {
            method: 'POST',
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Verification failed.");
        }
        
        statusIcon.className = 'fas fa-check-circle';
        statusIcon.style.color = 'var(--success-color)';
        statusHeading.textContent = 'Account Verified!';
        statusMessage.textContent = result.message;
        actionContainer.style.display = 'block';

    } catch (error) {
        statusIcon.className = 'fas fa-times-circle';
        statusIcon.style.color = 'var(--error-color)';
        statusHeading.textContent = 'Verification Failed';
        statusMessage.textContent = error.message;
        actionContainer.style.display = 'block';
    }
}

// --- FORGOT PASSWORD PAGE ---
function initForgotPasswordPage() {
    const form = document.getElementById('forgotPasswordForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('error-message');
        hideMessage('success-message');

        const email = document.getElementById('email').value;
        try {
            const response = await fetch('/api/v1/users/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });
            const result = await response.json();
            
            displayMessage('success-message', result.message, false);
            form.reset();

        } catch (error) {
            displayMessage('error-message', "An unexpected error occurred. Please try again.");
        }
    });
}

// RESET PASSWORD PAGE ---
function initResetPasswordPage() {
    const form = document.getElementById('resetPasswordForm');
    const newPasswordInput = document.getElementById('new_password');
    const confirmNewPasswordInput = document.getElementById('confirm_new_password');
    const strengthMeter = document.getElementById('password-strength-meter');
    const confirmFeedback = document.getElementById('password-confirm-feedback');
    
    if (!form) return;

    initPasswordToggles();
    newPasswordInput.addEventListener('input', () => updatePasswordStrengthVisuals(newPasswordInput, strengthMeter));
    newPasswordInput.addEventListener('input', () => updatePasswordMatchVisuals(newPasswordInput, confirmNewPasswordInput, confirmFeedback));
    confirmNewPasswordInput.addEventListener('input', () => updatePasswordMatchVisuals(newPasswordInput, confirmNewPasswordInput, confirmFeedback));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('error-message');
        hideMessage('success-message');

        const token = document.getElementById('reset_token').value;
        const new_password = newPasswordInput.value;
        const confirm_new_password = confirmNewPasswordInput.value;
        
        if (new_password !== confirm_new_password) {
            displayMessage('error-message', "Passwords do not match.");
            return;
        }

        try {
            const response = await fetch('/api/v1/users/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, new_password, confirm_new_password })
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || "Failed to reset password.");
            }

            const formContainer = document.querySelector('.form-container');
            if (formContainer) {
                formContainer.innerHTML = `
                    <div class="header" style="text-align: center;">
                         <i class="fas fa-check-circle" style="font-size: 4rem; color: var(--success-color); margin-bottom: 1.5rem;"></i>
                        <h2>Password Reset Successful!</h2>
                        <p>${result.message}</p>
                    </div>
                    <div class="footer" style="margin-top: 2rem;">
                        <a href="/" class="btn-primary" style="width: 100%; text-decoration: none; display: block; text-align: center; padding: 1rem;">Proceed to Login</a>
                    </div>
                `;
            }

        } catch (error) {
            displayMessage('error-message', error.message);
        }
    });
}


// --- PROFILE PAGE ---
function initProfilePage() {
    const logoutButton = document.getElementById('logoutButton');
    const changePasswordForm = document.getElementById('changePasswordForm');
    
    const openModalBtn = document.getElementById('openChangePasswordModal');
    const closeModalBtn = document.getElementById('closePasswordModal');
    const modalOverlay = document.getElementById('passwordModalOverlay');
    
    if (openModalBtn && closeModalBtn && modalOverlay) {
        openModalBtn.addEventListener('click', () => modalOverlay.classList.add('active'));

        const closeModal = () => {
            modalOverlay.classList.remove('active');
            changePasswordForm.reset();
            hideMessage('error-message');
            hideMessage('success-message');
        };

        closeModalBtn.addEventListener('click', closeModal);
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === "Escape" && modalOverlay.classList.contains('active')) closeModal();
        });
    }

    const newPasswordInput = document.getElementById('new_password');
    const confirmNewPasswordInput = document.getElementById('confirm_new_password');
    const strengthMeter = document.getElementById('password-strength-meter');
    const confirmFeedback = document.getElementById('password-confirm-feedback');
    
    initPasswordToggles();

    if (newPasswordInput && confirmNewPasswordInput && strengthMeter && confirmFeedback) {
        newPasswordInput.addEventListener('input', () => updatePasswordStrengthVisuals(newPasswordInput, strengthMeter));
        newPasswordInput.addEventListener('input', () => updatePasswordMatchVisuals(newPasswordInput, confirmNewPasswordInput, confirmFeedback));
        confirmNewPasswordInput.addEventListener('input', () => updatePasswordMatchVisuals(newPasswordInput, confirmNewPasswordInput, confirmFeedback));
    }

    logoutButton.addEventListener('click', async () => {
        try {
            await fetch('/api/v1/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            window.location.href = '/';
        }
    });

    changePasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('error-message');
        hideMessage('success-message');

        const old_password = document.getElementById('old_password').value;
        const new_password = document.getElementById('new_password').value;
        const confirm_new_password = document.getElementById('confirm_new_password').value;

        if (new_password !== confirm_new_password) {
            displayMessage('error-message', "New passwords do not match.");
            return;
        }

        try {
            const response = await fetch('/api/v1/users/me/change-password', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ old_password, new_password })
            });

            const result = await response.json();
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/unauthorized';
                    return;
                }
                throw new Error(result.detail || "An error occurred.");
            }

            displayMessage('success-message', 'Password updated successfully! You will be logged out.', false);
            setTimeout(() => {
                logoutButton.click();
            }, 2000);

        } catch (error) {
            displayMessage('error-message', error.message);
        }
    });

    fetchUserProfile();
}

async function fetchUserProfile() {
    try {
        const response = await fetch('/api/v1/users/me');

        if (!response.ok) {
            throw new Error('Session expired or invalid.');
        }

        const user = await response.json();
        document.getElementById('profileFullName').textContent = user.full_name || 'N/A';
        document.getElementById('profileUsername').textContent = user.username;
        document.getElementById('profileEmail').textContent = user.email;

    } catch (error) {
        console.error('Profile fetch error:', error);
        window.location.href = '/unauthorized';
    }
}