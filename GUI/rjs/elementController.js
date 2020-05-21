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
    }

    getChild(id) {
        return this.children[id];
    }

    hasProperty(property) {
        return typeof this.DOMTree[property] !== 'undefined';
    }

    render() {
        if (!this.hasProperty('element')) {
            this.element = document.createElement(this.DOMTree.type);
        }

        if (this.hasProperty('width')) {
            this.element.style.width = `${this.DOMTree.width}%`;
        }

        if (this.hasProperty('text')) {
            this.element.innerText = this.DOMTree.text;
        }

        if (this.hasProperty('classList')) {
            this.DOMTree.classList.forEach(nodeClass => {
                this.element.classList.add(nodeClass);
            });
        }

        Object.values(this.DOMTree.children).forEach(childNodeController => {
            childNodeController.render();
            this.element.appendChild(childNodeController.element);
        });
    }
}