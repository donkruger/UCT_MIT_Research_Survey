"""
Professional UI/UX Design System for Research Survey Application

This module implements a sophisticated design system following modern UI/UX best practices
with attention to typography, color theory, spacing, and micro-interactions.
"""

# Modern Typography System with Variable Fonts
GOOGLE_FONTS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');

/* Typography System */
:root {
    --font-primary: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-secondary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    
    /* Type Scale - Major Third (1.25) */
    --text-xs: 0.8rem;
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;
    --text-xl: 1.25rem;
    --text-2xl: 1.563rem;
    --text-3xl: 1.953rem;
    --text-4xl: 2.441rem;
    
    /* Font Weights */
    --font-light: 300;
    --font-regular: 400;
    --font-medium: 500;
    --font-semibold: 600;
    --font-bold: 700;
    
    /* Line Heights */
    --leading-tight: 1.25;
    --leading-normal: 1.5;
    --leading-relaxed: 1.75;
}

html, body, [class*="css"] {
    font-family: var(--font-secondary) !important;
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    font-weight: var(--font-regular);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: var(--font-primary) !important;
    font-weight: var(--font-semibold) !important;
    line-height: var(--leading-tight) !important;
    letter-spacing: -0.02em !important;
}

/* Optimized Text Sizes */
h1, .stMarkdown h1 { font-size: var(--text-4xl) !important; }
h2, .stMarkdown h2 { font-size: var(--text-3xl) !important; }
h3, .stMarkdown h3 { font-size: var(--text-2xl) !important; }
h4, .stMarkdown h4 { font-size: var(--text-xl) !important; }

/* Better paragraph spacing */
p {
    line-height: var(--leading-relaxed);
    margin-bottom: 1rem;
}

/* Code blocks with modern styling */
code, pre {
    font-family: var(--font-mono) !important;
    font-size: var(--text-sm) !important;
}
</style>
"""

# Modern Color System with Accessibility
COLOR_SYSTEM_CSS = """
<style>
:root {
    /* Primary Palette - Deep Blue to Purple Gradient */
    --primary-50: #f0f4ff;
    --primary-100: #e0e9ff;
    --primary-200: #c7d5ff;
    --primary-300: #a3b8ff;
    --primary-400: #7690ff;
    --primary-500: #4a69ff;
    --primary-600: #2a47f5;
    --primary-700: #1d35d8;
    --primary-800: #1a2eae;
    --primary-900: #1a2b89;
    
    /* Neutral Palette - Sophisticated Grays */
    --neutral-50: #fafbfc;
    --neutral-100: #f4f6f8;
    --neutral-200: #e9ecef;
    --neutral-300: #dde2e5;
    --neutral-400: #9ca3af;
    --neutral-500: #6b7280;
    --neutral-600: #4b5563;
    --neutral-700: #374151;
    --neutral-800: #1f2937;
    --neutral-900: #111827;
    
    /* Accent Colors */
    --accent-purple: #8b5cf6;
    --accent-blue: #3b82f6;
    --accent-teal: #06b6d4;
    --accent-green: #10b981;
    --accent-yellow: #f59e0b;
    --accent-red: #ef4444;
    
    /* Semantic Colors */
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-error: #ef4444;
    --color-info: #3b82f6;
    
    /* Spacing System - 8px Grid */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --space-2xl: 3rem;
    --space-3xl: 4rem;
    
    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-2xl: 1.5rem;
    --radius-full: 9999px;
    
    /* Shadows - Subtle and Elegant */
    --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    
    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --primary-50: #1a2b89;
        --primary-900: #f0f4ff;
        --neutral-50: #111827;
        --neutral-900: #fafbfc;
    }
}
</style>
"""

# Animated Gradient Title with Premium Feel
GRADIENT_TITLE_CSS = """
<style>
@keyframes gradient-shift {
    0%, 100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}

@keyframes subtle-glow {
    0%, 100% {
        filter: brightness(1) drop-shadow(0 0 20px rgba(74, 105, 255, 0.3));
    }
    50% {
        filter: brightness(1.05) drop-shadow(0 0 30px rgba(74, 105, 255, 0.5));
    }
}

.gradient-title {
    font-family: var(--font-primary) !important;
    font-size: clamp(2rem, 5vw, 3.5rem) !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    letter-spacing: -0.03em !important;
    margin: 1.5rem 0 2rem 0 !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #667eea 75%, #764ba2 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: gradient-shift 8s ease infinite, subtle-glow 4s ease-in-out infinite !important;
    text-align: left !important;
    display: inline-block !important;
}

/* Subtitle styling */
.subtitle {
    font-family: var(--font-secondary);
    font-size: var(--text-lg);
    color: var(--neutral-600);
    font-weight: var(--font-regular);
    line-height: var(--leading-relaxed);
    margin-top: -1rem;
    margin-bottom: 2rem;
}
</style>
"""

# Smooth Page Transitions and Animations
ANIMATIONS_CSS = """
<style>
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

/* Main content animation */
.main .block-container {
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Stagger animations for elements */
.element-container:nth-child(1) { animation-delay: 0ms; }
.element-container:nth-child(2) { animation-delay: 50ms; }
.element-container:nth-child(3) { animation-delay: 100ms; }
.element-container:nth-child(4) { animation-delay: 150ms; }
.element-container:nth-child(5) { animation-delay: 200ms; }

/* Smooth hover transitions */
a, button, .stButton > button, [role="button"] {
    transition: all var(--transition-base) !important;
}

/* Loading skeleton animation */
.skeleton {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    background: linear-gradient(90deg, var(--neutral-200) 25%, var(--neutral-300) 50%, var(--neutral-200) 75%);
    background-size: 200% 100%;
}
</style>
"""

# Modern Form Styling with Focus States
FORM_STYLING_CSS = """
<style>
/* Input Field Styling */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    font-family: var(--font-secondary) !important;
    font-size: var(--text-base) !important;
    border: 2px solid var(--neutral-200) !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.75rem 1rem !important;
    background-color: white !important;
    transition: all var(--transition-base) !important;
    box-shadow: var(--shadow-xs) !important;
}

/* Focus states with accessibility */
.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--primary-500) !important;
    box-shadow: 0 0 0 3px rgba(74, 105, 255, 0.1), var(--shadow-sm) !important;
    outline: none !important;
}

/* Hover states */
.stTextInput > div > div > input:hover,
.stSelectbox > div > div > select:hover,
.stTextArea > div > div > textarea:hover,
.stNumberInput > div > div > input:hover {
    border-color: var(--primary-300) !important;
}

/* Labels with better typography */
.stTextInput > label,
.stSelectbox > label,
.stTextArea > label,
.stNumberInput > label,
.stCheckbox > label {
    font-family: var(--font-secondary) !important;
    font-size: var(--text-sm) !important;
    font-weight: var(--font-medium) !important;
    color: var(--neutral-700) !important;
    margin-bottom: var(--space-sm) !important;
    letter-spacing: 0.01em !important;
}

/* Help text styling */
.stTextInput > div > div > small,
.stSelectbox > div > div > small {
    font-size: var(--text-xs) !important;
    color: var(--neutral-500) !important;
    margin-top: var(--space-xs) !important;
}

/* Checkbox and Radio styling */
.stCheckbox > label > div:first-child,
.stRadio > label > div:first-child {
    border: 2px solid var(--neutral-300) !important;
    transition: all var(--transition-base) !important;
}

.stCheckbox > label > div:first-child:hover,
.stRadio > label > div:first-child:hover {
    border-color: var(--primary-400) !important;
    transform: scale(1.05);
}

/* Success/Error states */
.st-success {
    background-color: rgba(16, 185, 129, 0.1) !important;
    border-left: 4px solid var(--color-success) !important;
}

.st-error {
    background-color: rgba(239, 68, 68, 0.1) !important;
    border-left: 4px solid var(--color-error) !important;
}
</style>
"""

# Premium Button Styling
BUTTON_STYLING_CSS = """
<style>
/* Primary button with gradient */
.stButton > button {
    font-family: var(--font-secondary) !important;
    font-weight: var(--font-medium) !important;
    font-size: var(--text-base) !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: var(--radius-lg) !important;
    border: none !important;
    background: linear-gradient(135deg, var(--primary-500) 0%, var(--accent-purple) 100%) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
    transition: all var(--transition-base) !important;
    position: relative !important;
    overflow: hidden !important;
    letter-spacing: 0.02em !important;
}

/* Hover effect with transform */
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
    background: linear-gradient(135deg, var(--primary-600) 0%, var(--accent-purple) 100%) !important;
}

/* Active state */
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Ripple effect on click */
.stButton > button::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.stButton > button:active::after {
    width: 300px;
    height: 300px;
}

/* Secondary button variant */
.stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--primary-600) !important;
    border: 2px solid var(--primary-200) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--primary-50) !important;
    border-color: var(--primary-300) !important;
}

/* Disabled state */
.stButton > button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}
</style>
"""

# Card and Container Styling
CONTAINER_STYLING_CSS = """
<style>
/* Main container with max-width for readability */
.main .block-container {
    max-width: 1200px !important;
    padding: 2rem 3rem !important;
    margin: 0 auto !important;
}

/* Card-like sections */
.stExpander {
    border: 1px solid var(--neutral-200) !important;
    border-radius: var(--radius-xl) !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: var(--space-lg) !important;
    overflow: hidden !important;
    transition: all var(--transition-base) !important;
    background: white !important;
}

.stExpander:hover {
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px);
}

/* Expander header styling */
.stExpander > details > summary {
    padding: var(--space-lg) !important;
    font-weight: var(--font-medium) !important;
    font-size: var(--text-lg) !important;
    background: var(--primary-600) !important;  /* Solid blue instead of gradient */
    color: white !important;  /* White text for contrast */
    border-radius: var(--radius-lg) !important;
}

.stExpander > details[open] > summary {
    border-bottom: 1px solid var(--neutral-200);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0 !important;
}

/* Info boxes with gradient borders */
.stAlert {
    border-radius: var(--radius-lg) !important;
    border: none !important;
    padding: var(--space-lg) !important;
    background: white !important;
    box-shadow: var(--shadow-sm) !important;
    position: relative !important;
}

.stAlert::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary-400), var(--accent-purple));
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

/* Metric cards */
.metric-container {
    background: white;
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--neutral-200);
    transition: all var(--transition-base);
}

.metric-container:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* Section dividers */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(to right, transparent, var(--neutral-300), transparent) !important;
    margin: var(--space-2xl) 0 !important;
}
</style>
"""

# Progress Indicators and Loading States
PROGRESS_STYLING_CSS = """
<style>
/* Progress bar with gradient */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--primary-400), var(--accent-purple)) !important;
    border-radius: var(--radius-full) !important;
    height: 8px !important;
    animation: shimmer 2s infinite !important;
}

@keyframes shimmer {
    0% {
        opacity: 0.8;
    }
    50% {
        opacity: 1;
    }
    100% {
        opacity: 0.8;
    }
}

/* Step indicator */
.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: var(--space-xl) 0;
}

.step {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--neutral-200);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: var(--font-semibold);
    color: var(--neutral-500);
    position: relative;
    transition: all var(--transition-base);
}

.step.active {
    background: linear-gradient(135deg, var(--primary-500), var(--accent-purple));
    color: white;
    transform: scale(1.1);
    box-shadow: var(--shadow-lg);
}

.step.completed {
    background: var(--color-success);
    color: white;
}

.step-connector {
    width: 100px;
    height: 2px;
    background: var(--neutral-200);
    margin: 0 var(--space-sm);
}

.step-connector.completed {
    background: var(--color-success);
}
</style>
"""

# Responsive Design
RESPONSIVE_CSS = """
<style>
/* Mobile optimizations */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem !important;
    }
    
    .gradient-title {
        font-size: 2rem !important;
    }
    
    .stButton > button {
        width: 100% !important;
        padding: 1rem !important;
    }
    
    .stColumns > div {
        margin-bottom: var(--space-md);
    }
}

/* Tablet optimizations */
@media (min-width: 768px) and (max-width: 1024px) {
    .main .block-container {
        padding: 1.5rem 2rem !important;
    }
}

/* Large screen optimizations */
@media (min-width: 1920px) {
    .main .block-container {
        max-width: 1400px !important;
    }
}

/* Print styles */
@media print {
    .stButton,
    .stSidebar,
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    .main .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
}
</style>
"""

# Accessibility Enhancements
ACCESSIBILITY_CSS = """
<style>
/* Focus visible for keyboard navigation */
*:focus-visible {
    outline: 3px solid var(--primary-500) !important;
    outline-offset: 2px !important;
}

/* Skip to main content link */
.skip-to-main {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--primary-600);
    color: white;
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-md);
    text-decoration: none;
    z-index: 100;
}

.skip-to-main:focus {
    top: 10px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    * {
        border-width: 2px !important;
    }
    
    .stButton > button {
        border: 2px solid currentColor !important;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    * {
        animation: none !important;
        transition: none !important;
    }
}

/* Screen reader only text */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
</style>
"""

# Combine all styles for easy import
def get_all_styles():
    """Return all CSS styles combined."""
    return (
        GOOGLE_FONTS_CSS +
        COLOR_SYSTEM_CSS +
        GRADIENT_TITLE_CSS +
        ANIMATIONS_CSS +
        FORM_STYLING_CSS +
        BUTTON_STYLING_CSS +
        CONTAINER_STYLING_CSS +
        PROGRESS_STYLING_CSS +
        RESPONSIVE_CSS +
        ACCESSIBILITY_CSS
    )

# Legacy exports for compatibility
FADE_IN_CSS = ANIMATIONS_CSS  # Maintain compatibility with existing code