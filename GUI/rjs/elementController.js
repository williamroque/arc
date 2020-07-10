class ElementController {
    constructor(type, properties) {
        this.DOMTree = {
            type: type,
            ...properties,
            children: {}
        };
        this.childID = 0;

        this.rendersText = true;

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
        node.nodeID = id;

        this.DOMTree.children[id] = node;

        this.render();

        return id;
    }

    removeChild(id) {
        this.DOMTree.children[id].remove();
        delete this.DOMTree.children[id];
    }

    toggleText() {
        this.rendersText = !this.rendersText;
        this.render();
    }

    query(id) {
        if (id in this.DOMTree.children) {
            return this.DOMTree.children[id];
        }

        const target = Object.values(this.DOMTree.children).find(child => child.query(id));
        return target ? target.query(id) : undefined;
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

        if ('text' in this.DOMTree && this.rendersText) {
            this.element.innerText = this.DOMTree.text;
        } else {
            this.element.innerText = '';
        }

        if ('classList' in this.DOMTree) {
            this.element.className = '';
            for (const nodeClass of this.DOMTree.classList) {
                this.element.classList.add(nodeClass);
            }
        }

        for (const childNode of Object.values(this.DOMTree.children)) {
            childNode.render();
            this.element.appendChild(childNode.element);
        }
    }

    remove() {
        this.element.remove();
    }
}