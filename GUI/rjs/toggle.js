const togglePrompt = document.querySelector('#toggle-prompt');

class Toggle {
    static clearPrompt() {
        let child;
        while (child = togglePrompt.firstChild) {
            togglePrompt.removeChild(child);
        }
    }

    static show(buttons, x, y) {
        Toggle.clearPrompt();

        buttons.forEach(button => {
            button.addEventListener('click', function() {
                Toggle.hide();
            }, null);
            togglePrompt.appendChild(button.element);
        });

        if (x + togglePrompt.offsetWidth > window.innerWidth) {
            x -= togglePrompt.offsetWidth;
        }

        if (y + togglePrompt.offsetHeight > window.innerHeight) {
            y -= togglePrompt.offsetHeight;
        }

        togglePrompt.style.left = `${x}px`;
        togglePrompt.style.top = `${y}px`;

        togglePrompt.classList.remove('hidden');
    }

    static hide() {
        togglePrompt.classList.add('hidden');
    }
}

window.addEventListener('click', () => Toggle.hide(), false);
window.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        Toggle.hide();
    }
}, false);
togglePrompt.addEventListener('click', e => e.stopPropagation(), false);