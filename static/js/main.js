/**
 * TravelEase - Custom JavaScript
 * =================================
 * This file handles:
 *   1. Form validation for booking & registration
 *   2. AJAX seat availability polling
 *   3. Smooth scroll behavior
 *   4. Alert auto-dismiss
 *   5. Date input minimum (prevent past-date selection)
 *   6. Number input restrictions (positive integers only)
 *
 * All logic is wrapped in an IIFE (Immediately Invoked Function Expression)
 * to avoid polluting the global namespace and prevent variable collisions.
 */

(function () {
    'use strict';

    // =========================================================================
    // 1. DOM READY HANDLER
    // All initialization code runs after the DOM is fully parsed. This ensures
    // that querySelector calls find their targets before we try to bind events.
    // =========================================================================
    document.addEventListener('DOMContentLoaded', function () {
        initDateRestrictions();
        initAlertDismiss();
        initSmoothScroll();
        initNumericInputs();
        initPasswordMatch();
        initOTPAutoSubmit();
        initBookingFormValidation();
        initSearchFormPersistence();
    });

    // =========================================================================
    // 2. DATE RESTRICTIONS
    // Sets the min attribute on date inputs to today's date. This prevents
    // users from searching for or booking past dates, which would be invalid.
    // Uses the user's local date in YYYY-MM-DD format.
    // =========================================================================
    function initDateRestrictions() {
        var dateInputs = document.querySelectorAll('input[type="date"]');
        if (dateInputs.length === 0) return;

        var today = new Date();
        var yyyy = today.getFullYear();
        var mm = String(today.getMonth() + 1).padStart(2, '0');
        var dd = String(today.getDate()).padStart(2, '0');
        var todayStr = yyyy + '-' + mm + '-' + dd;

        dateInputs.forEach(function (input) {
            if (!input.hasAttribute('min')) {
                input.setAttribute('min', todayStr);
            }
        });
    }

    // =========================================================================
    // 3. AUTO-DISMISS ALL ALERTS
    // All Bootstrap alerts (Django messages + JS toasts) auto-dismiss after
    // 8 seconds. Uses a smooth slide-up + fade-out animation. Includes both
    // .alert-dismissible (Django messages framework) and plain .alert elements.
    // =========================================================================
    function initAlertDismiss() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            setTimeout(function () {
                // Start the fade-out + slide-up animation
                alert.style.transition =
                    'opacity 0.6s ease, transform 0.6s ease, margin 0.6s ease, padding 0.6s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                alert.style.marginTop = '0';
                alert.style.marginBottom = '0';
                alert.style.paddingTop = '0';
                alert.style.paddingBottom = '0';
                // Remove from DOM after animation completes
                setTimeout(function () {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 600);
            }, 8000);
        });
    }

    // =========================================================================
    // 4. SMOOTH SCROLL
    // Intercepts anchor links that point to on-page targets (#id) and animates
    // the scroll instead of jumping instantly. Respects prefers-reduced-motion.
    // =========================================================================
    function initSmoothScroll() {
        var mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        if (mediaQuery.matches) return; // Respect accessibility preference

        document.addEventListener('click', function (e) {
            var link = e.target.closest('a[href^="#"]');
            if (!link) return;

            var targetId = link.getAttribute('href');
            if (targetId === '#') return;

            var target = document.querySelector(targetId);
            if (!target) return;

            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    }

    // =========================================================================
    // 5. NUMERIC INPUT RESTRICTIONS
    // Ensures number inputs (like total_seats, price) only accept positive
    // integers. Blocks typing of 'e', '-', '+', '.' which HTML number inputs
    // normally allow but are meaningless for counts/prices.
    // =========================================================================
    function initNumericInputs() {
        document.addEventListener('keydown', function (e) {
            var input = e.target;
            // Only filter inputs with data-integer attribute or type=number
            // that are meant for whole numbers
            if (input.type !== 'number') return;
            if (input.dataset.allowDecimal === 'true') return;

            // Block non-numeric keys: e (scientific notation), minus, plus, dot
            var blockedKeys = ['e', 'E', '-', '+', '.'];
            if (blockedKeys.includes(e.key)) {
                e.preventDefault();
            }
        });
    }

    // =========================================================================
    // 6. PASSWORD MATCH VALIDATION
    // Live validation on the registration form: checks that password and
    // confirm_password fields match. Shows visual feedback via Bootstrap's
    // is-valid/is-invalid classes.
    // =========================================================================
    function initPasswordMatch() {
        var password1 = document.querySelector('input[name="password1"]');
        var password2 = document.querySelector('input[name="password2"]');
        if (!password1 || !password2) return;

        function checkMatch() {
            if (password2.value.length === 0) {
                password2.classList.remove('is-valid', 'is-invalid');
                return;
            }
            if (password1.value === password2.value) {
                password2.classList.add('is-valid');
                password2.classList.remove('is-invalid');
            } else {
                password2.classList.add('is-invalid');
                password2.classList.remove('is-valid');
            }
        }

        password1.addEventListener('input', checkMatch);
        password2.addEventListener('input', checkMatch);
    }

    // =========================================================================
    // 7. OTP AUTO-SUBMIT
    // When the user types the 6th digit in the OTP input, automatically submit
    // the form — saves a click and improves UX flow.
    // =========================================================================
    function initOTPAutoSubmit() {
        var otpInput = document.querySelector('.otp-input');
        if (!otpInput) return;

        otpInput.addEventListener('input', function () {
            // Only numbers, max 6 digits
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);

            if (this.value.length === 6) {
                var form = this.closest('form');
                if (form) {
                    // Small delay so user sees the last digit appear
                    setTimeout(function () {
                        form.submit();
                    }, 300);
                }
            }
        });
    }

    // =========================================================================
    // 8. BOOKING FORM VALIDATION
    // Before submitting the bus/flight booking form, validates that:
    //   - A seat has been selected
    //   - Passenger name is not empty
    //   - Contact number is provided
    // =========================================================================
    function initBookingFormValidation() {
        var bookingForm = document.querySelector('#booking-form');
        if (!bookingForm) return;

        bookingForm.addEventListener('submit', function (e) {
            var selectedSeat = document.querySelector('#selected-seat');
            var seatValue = selectedSeat ? selectedSeat.value : '';

            if (!seatValue) {
                e.preventDefault();
                showToast('Please select a seat before booking.', 'warning');
                return false;
            }

            var passengerName = document.querySelector('#passenger-name');
            if (passengerName && !passengerName.value.trim()) {
                e.preventDefault();
                passengerName.focus();
                showToast('Please enter the passenger name.', 'warning');
                return false;
            }

            var contactNumber = document.querySelector('#contact-number');
            if (contactNumber && !contactNumber.value.trim()) {
                e.preventDefault();
                contactNumber.focus();
                showToast('Please enter a contact number.', 'warning');
                return false;
            }

            // Disable button to prevent double-submission
            var submitBtn = bookingForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            }
        });
    }

    // =========================================================================
    // 9. SEARCH FORM PERSISTENCE
    // Remembers the last search values in sessionStorage and pre-fills the
    // search form when navigating back from results.
    // =========================================================================
    function initSearchFormPersistence() {
        var searchForm = document.querySelector('#search-form');
        if (!searchForm) return;

        // Restore saved values
        var savedDeparture = sessionStorage.getItem('te_search_departure');
        var savedDestination = sessionStorage.getItem('te_search_destination');
        var savedDate = sessionStorage.getItem('te_search_date');

        var departureInput = searchForm.querySelector('input[name="departure"]');
        var destinationInput = searchForm.querySelector('input[name="destination"]');
        var dateInput = searchForm.querySelector('input[name="date"]');

        if (departureInput && savedDeparture) departureInput.value = savedDeparture;
        if (destinationInput && savedDestination) destinationInput.value = savedDestination;
        if (dateInput && savedDate) dateInput.value = savedDate;

        // Save on submit
        searchForm.addEventListener('submit', function () {
            if (departureInput) sessionStorage.setItem('te_search_departure', departureInput.value);
            if (destinationInput) sessionStorage.setItem('te_search_destination', destinationInput.value);
            if (dateInput) sessionStorage.setItem('te_search_date', dateInput.value);
        });
    }

    // =========================================================================
    // 10. TOAST NOTIFICATION HELPER
    // Displays a Bootstrap-style toast at the top-right of the screen.
    // Used by form validation to show non-intrusive feedback messages.
    // =========================================================================
    function showToast(message, type) {
        type = type || 'info';

        var bgClass = 'bg-info';
        if (type === 'warning') bgClass = 'bg-warning text-dark';
        if (type === 'error') bgClass = 'bg-danger';
        if (type === 'success') bgClass = 'bg-success';

        var container = document.querySelector('#toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText =
                'position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;';
            document.body.appendChild(container);
        }

        var toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white border-0 ' + bgClass;
        toast.setAttribute('role', 'alert');
        toast.innerHTML =
            '<div class="d-flex"><div class="toast-body">' +
            message +
            '</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>';

        container.appendChild(toast);

        // Use Bootstrap Toast API if available, otherwise manual dismiss
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            var bsToast = new bootstrap.Toast(toast, { delay: 4000 });
            bsToast.show();
        } else {
            setTimeout(function () {
                toast.style.transition = 'opacity 0.3s ease';
                toast.style.opacity = '0';
                setTimeout(function () {
                    if (toast.parentNode) toast.parentNode.removeChild(toast);
                }, 300);
            }, 4000);
        }
    }

    // =========================================================================
    // 11. SEAT SELECTION HELPER (Exported for inline onclick usage)
    // The seat selection functions in bus_detail.html and flight_detail.html
    // call this central handler. It updates the hidden input, toggles visual
    // states, and enables/disables the book button.
    // =========================================================================
    window.selectSeat = function (button, seatNumber, type) {
        type = type || 'bus';

        // Deselect all seats of this type first
        var selector = type === 'flight' ? '.seat-btn-fl' : '.seat-btn';
        var allSeats = document.querySelectorAll(selector);
        allSeats.forEach(function (s) { s.classList.remove('selected'); });

        // Select clicked seat
        button.classList.add('selected');

        // Update hidden input value
        var hiddenInput = document.querySelector('#selected-seat');
        if (hiddenInput) hiddenInput.value = seatNumber;

        // Update display element
        var seatDisplay = document.querySelector('#selected-seat-display');
        if (seatDisplay) seatDisplay.textContent = 'Seat: ' + seatNumber;

        // Enable book button
        var bookBtn = document.querySelector('#book-btn');
        if (bookBtn) {
            bookBtn.disabled = false;
            bookBtn.classList.remove('btn-secondary');
            bookBtn.classList.add('btn-success');
        }
    };

})();