class ElementController {
    constructor(type, properties) {
        this.DOMTree = {
            type: type,
            ...properties,
            children: {}
        };
        this.childID = 0;

        this.render();
    }

    addClass(nodeClass) {
        if ('classList' in this.DOMTree) {
            this.DOMTree.classList.add(nodeClass);
        } else {
            this.DOMTree.classList = new Set([nodeClass]);
        }
        this.render();
    }

    removeClass(nodeClass) {
        if ('classList' in this.DOMTree) {
            this.DOMTree.classList.delete(nodeClass);
            this.render();
        }
    }

    addChild(node, id) {
        if (typeof id === "undefined") {
            id = `unique-${this.childID++}`;
        }
        this.DOMTree.children[id] = node;

        this.render();

        return id;
    }

    removeChild(id) {
        this.DOMTree.children[id].remove();
        delete this.DOMTree.children[id];
    }

    getChild(id) {
        return this.DOMTree.children[id];
    }

    addEventListener(event, callback, context) {
        this.element.addEventListener(event, callback.bind(context), false);
    }

    render() {
        if (!this.element) {
            this.element = document.createElement(this.DOMTree.type);
        }

        if ('width' in this.DOMTree) {
            this.element.style.width = `${this.DOMTree.width}%`;
        }

        if ('text' in this.DOMTree) {
            this.element.innerText = this.DOMTree.text;
        }

        if ('classList' in this.DOMTree) {
            this.element.className = '';
            this.DOMTree.classList.forEach(nodeClass => {
                this.element.classList.add(nodeClass);
            });
        }

        Object.values(this.DOMTree.children).forEach(childNodeController => {
            childNodeController.render();
            this.element.appendChild(childNodeController.element);
        });
    }

    remove() {
        this.element.remove();
    }
}