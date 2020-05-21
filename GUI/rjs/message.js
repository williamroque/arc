class Message {
    constructor(message) {
        this.message = message;
        this.messagePrompt = document.querySelector('#message-prompt');
    }

    show(t, previous) {
        this.messagePrompt.innerHTML = this.message;
        this.messagePrompt.style.display = 'block';
        this.setInterval(() => {
            
        }, t);
    }
}