> [!WARNING]
> The API changed significantly in version 4.0.0. See [Porting to TkinterWeb v4+](UPGRADING.md) for details.

> [!IMPORTANT]
> The TkinterWeb documentation has moved to https://tkinterweb.readthedocs.io/en/latest/index.html. See you there!

## DOM Manipulation with TkinterWeb

## Overview
**TkinterWeb provides a handful of functions that allow for manipulation of the webpage. They are fashioned after common JavaScript functions.**

## How-To
To manipulate the Document Object Model, use `HtmlFrame.document` (new since version 3.25). For example, to create a heading with blue text inside of a container with the id 'container', one can use the following:
```
yourhtmlframe = tkinterweb.HtmlFrame(root)
yourhtmlframe.load_html("<div id='container'><p>Test</p></div>")
container = yourhtmlframe.document.getElementById("container")
new_header = yourhtmlframe.document.createElement("h1")
new_header.textContent = "Hello, world!"
new_header.style.color = "blue"
container.appendChild(new_header)
```
To register a callback for `<script>` elements, use the `on_script` parameter:
```
yourhtmlframe = tkinterweb.HtmlFrame(root)
yourhtmlframe.load_html("<div id='container'><script>// Do stuff</script><p>Test</p></div>")
def handle_scripts(attributes, tagcontents):
    ## Do stuff
yourhtmlframe.configure(on_script=handle_scripts)
```

## API Reference

### Key Properties:
#### `document.body` property
Return the document's body element.

Return type
* *HTMLElement*

---
#### `document.documentElement` property
Return the document's root element.

Return type
* *HTMLElement*

---
### Key Methods:
#### `document.createElement(tagname)`
Create a new HTML element with the given tag name.

Parameters
* **tagname** *(string)* - Specifies the new element's HTML tag.

Return type
* *HTMLElement*

---
#### `document.createTextNode(text)`
Create a new text node with the given text content.

Parameters
* **text** *(string)* - Specifies the text content of the new node.

Return type
* *HTMLElement*

---
#### `document.getElementById(query)`
Return an element given an id.

Parameters
* **query** *(string)* - Specifies the element id to be searched for .

Return type
* *HTMLElement*

---
#### `document.getElementsByClassName(query)`
Return all elements that match given a class name.

Parameters
* **query** *(string)* - Specifies the class to be searched for. 

Return type
* *HTMLElement*

---
#### `document.getElementsByName(query)`
Return all elements that match a given name attribute.

Parameters
* **query** *(string)* - Specifies the name to be searched for.

Return type
* *tuple*

---
#### `document.getElementsByTagName(query)`
Return all elements that match a given tag name.

Parameters
* **query** *(string)* - Specifies the tag to be searched for.

Return type
* *tuple*

---
#### `document.querySelector(query)`
Return the first element that matches a given CSS selector.

Parameters
* **query** *(string)* - Specifies the CSS selector to be searched for.

Return type
* *HTMLElement*

---
#### `document.querySelectorAll(query)`
Return all elements that match a given CSS selector.

Parameters
* **query** *(string)* - Specifies the CSS selector to be searched for.

Return type
* *tuple*

---
## HTMLElement API 

### Key Variables:
* `html`: The element's corresponding TkinterWeb instance.
* `node`: The Tkhtml node associated with the element.

### Key Properties:
#### `innerHTML` property
Get and set the inner HTML of an element.

---
#### `textContent` property
Get and set the text content of an element.

Return type
* *string*

---
#### `tagName` property
Get the tag name of the element.

Return type
* *string*

---
#### `attributes` property
Get the attributes of the element.

Return type
* *string*

---
#### `style` property
Manage the element's styling.

Return type
* *CSSStyleDeclaration*

---
#### `parentElement` property
Get the element's parent element.

Return type
* *HTMLElement*

---
#### `children` property
Get the element's children elements.

Return type
* *tuple*

---
### Key Methods:
#### `getAttribute(attribute)`
Get the value of the given attribute.

Parameters
* **attribute** *(string)* - Specifies the attribute to return.

Return type
* *string*

---
#### `setAttribute(attribute, value)`
Set the value of the given attribute.

Parameters
* **attribute** *(string)* - Specifies the attribute to set.
* **value** *(string)* - Specifies the new value of the specified attribute.

Return type
* *string*

---
#### `remove()`
Delete the element.

---
#### `appendChild(children)`
Insert the specified children into the element.

Parameters
* **children** *(list, tuple, or HTMLElement)* - Specifies the element(s) to be added into the element.

---
#### `insertBefore(children, before)`
Insert the specified children before a specified child element.

Parameters
* **children** *(list, tuple, or HTMLElement)* - Specifies the element(s) to be added into the element.
* **before** *(HTMLElement)* - Specifies the child element that the added elements should be placed before.

---
#### `getElementById(query)`
Return an element that is a child of the current element and matches the given id.

Parameters
* **query** *(string)* - Specifies the element id to be searched for.

Return type
* *HTMLElement*

---
#### `getElementsByClassName(query)`
Return all elements that are children of the current element and match the given class name.

Parameters
* **query** *(string)* - Specifies the class to be searched for.

Return type
* *HTMLElement*

---
#### `getElementsByName(query)`
Return all elements that are children of the current element and match the given name attribute.

Parameters
* **query** *(string)* - Specifies the name to be searched for.

Return type
* *tuple*

---
#### `getElementsByTagName(query)`
Return all elements that are children of the current element and match the given tag name.

Parameters
* **query** *(string)* - Specifies the tag to be searched for.

Return type
* *tuple*

---
#### `querySelector(query)`
Return the first element that are children of the current element and match the given CSS selector.

Parameters
* **query** *(string)* - Specifies the CSS selector to be searched for.

Return type
* *HTMLElement*

---
#### `querySelectorAll(query)`
Return all elements that are children of the current element and match the given CSS selector.

Parameters
* **query** *(string)* - Specifies the CSS selector to be searched for.

Return type
* *tuple*

---
#### `scrollIntoView()`
Scroll the viewport so that this element is visible.

---
## CSSStyleDeclaration API 

### Key Variables:
* `html`: The element's corresponding TkinterWeb instance.
* `node`: The Tkhtml node associated with the element


### Key Properties:
**All camel-cased supported CSS properties are valid properties.**
Examples include `color`, `backgroundColor`, and `fontFamily`.

CSS properties can also be returned or set as key-value pairs (eg. `CSSStyleDeclaration["background-color"]`)

---
#### `cssText` property
Get the text of the element's inline style declaration. Read-only.

Return type
* *string*

---
#### `length` property
Get the number of style declarations in the element's inline style declaration. Read-only.

Return type
* *int*

---
#### `cssProperties` property
Get all computed properties for the element. Read-only.

Return type
* *dict*

---
#### `cssInlineProperties` property
Get all inline properties for the element. Similar to the `cssText` property, but formatted as a dictionary. Read-only.

Return type
* *dict*

---

Please report bugs or request new features on the [issues page](https://github.com/Andereoo/TkinterWeb/issues).

Special thanks to [Zamy846692](https://github.com/Zamy846692) for the help making this happen!
