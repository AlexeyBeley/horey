function selectGTEMOption(root) {
    if (!root) return false;

    // Find all elements containing GTEM text
    const allNodes = Array.from(root.querySelectorAll('*'));
    for (let el of allNodes) {
        if (el.children.length === 0 && el.textContent && el.textContent.includes('GTEM')) {

            // Walk up the DOM to find the clickable list item wrapper
            let target = el;
            while (target && target !== document.body) {
                // Look for common Angular dropdown item roles or classes
                if (target.getAttribute('role') === 'option' ||
                    target.classList.contains('q-dropmenu-item') ||
                    target.tagName.toLowerCase().includes('item') ||
                    target.tagName.toLowerCase().includes('option')) {
                    break;
                }
                target = target.parentElement;
            }

            // If no wrapper found, fallback to element 3 levels up
            if (!target || target === document.body) {
                target = el.parentElement?.parentElement || el;
            }

            // Fire full event chain so Angular registers the click
            ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach(eventType => {
                target.dispatchEvent(new MouseEvent(eventType, {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
            });

            return true;
        }
    }

    // Pierce Shadow DOM
    for (let child of root.querySelectorAll('*')) {
        if (child.shadowRoot) {
            if (selectGTEMOption(child.shadowRoot)) return true;
        }
    }
    return false;
}

selectGTEMOption(document);