/**
 * Toast Notification System
 * Non-blocking, accessible toast notifications
 */

export class Toast {
  constructor() {
    this.container = null;
    this.initContainer();
  }

  initContainer() {
    // Create toast container if it doesn't exist
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.setAttribute('role', 'region');
      this.container.setAttribute('aria-live', 'polite');
      this.container.setAttribute('aria-atomic', 'true');
      document.body.appendChild(this.container);
    }
  }

  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    
    // Determine icon based on type
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'warning') icon = '⚠️';
    if (type === 'error') icon = '❌';
    if (type === 'info') icon = 'ℹ️';

    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" aria-label="Close notification">&times;</button>
    `;

    // Close button functionality
    toast.querySelector('.toast-close').addEventListener('click', () => {
      this.removeToast(toast);
    });

    this.container.appendChild(toast);

    // Auto-dismiss
    if (duration > 0) {
      setTimeout(() => {
        this.removeToast(toast);
      }, duration);
    }

    return toast;
  }

  removeToast(toast) {
    toast.classList.add('toast-exit');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  success(message, duration = 3000) {
    return this.show(message, 'success', duration);
  }

  error(message, duration = 3000) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration = 3000) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration = 3000) {
    return this.show(message, 'info', duration);
  }
}

// Create singleton instance
export const toast = new Toast();
