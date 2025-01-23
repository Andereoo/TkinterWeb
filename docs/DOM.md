## DOM Manipulation with WkinterWeb

## Overview
TkinterWeb provides a handful of functions that allow for manipulation of the webpage. They are fashioned after common JavaScript functions.

## How-To
To manipulate the Document Object Model, use `yourframe.document`. For example to create a heading inside of a container with the id 'container', one can use the following:
```
yourframe = tkinterweb.HtmlFrame(root)
yourframe.load_html("<div id='container'><p>Test</p></div>")
container = yourframe.document.getElementById("container")
new_header = yourframe.document.createElement("h1")
new_header.textContent("Hello, world!")
container.appendChild(new_header)
```
The above code will replace the `<div>` element with the `mybutton` Button. This `<div>` element will still behave as it would normally. This means that it is very easy to set the location of the button, the size, and much more using CSS. For example, `<div style="width:50px" widgetid="+str(mybutton)+"></div>` would make the button exactly 50 pixels wide.
  
Add the attribute `allowscrolling="yes"` to allow scrolling the document when the mouse is over the button. Note that this has no effect on the HtmlLabel widget.

## API Reference

#### `document.createElement(tagname)`
Create a new HTML element with the specified tag name

Parameters
* **tagname** *(string)* - Specifies the new element's HTML tag

Return type
* *HtmlElement*

---

#### `document.createTextNode(text)`
Create a new text node with the given text conent

Parameters
* **text** *(string)* - Specifies the text content of the new node

Return type
* *HtmlElement*

---

#### `document.body()`
Return the document's body element

Return type
* *HtmlElement*

---

#### `document.getElementById(query)`
Return an element given an id

Parameters
* **query** *(string)* - Specifies the element id to be searched for 

Return type
* *HtmlElement*

---

#### `document.getElementsByClassName(query)`
Return a list of elements given a class name

Parameters
* **query** *(string)* - Specifies the class name to be searched for 

Return type
* *HtmlElement*

---

#### `document.getElementsByName(query)`
Return a list of elements matching a given name attribute

Parameters
* **query** *(string)* - Specifies the name to be searched for 

Return type
* *list*

---

#### `document.getElementsByTagName(query)`
Return a list of elements matching a given tag name

Parameters
* **query** *(string)* - Specifies the tag name to be searched for 

Return type
* *list*

---

#### `document.querySelector(query)`
Return the first element that matches a given CSS selector

Parameters
* **query** *(string)* - Specifies the CSS selector to be searched for 

Return type
* *HtmlElement*

---

#### `document.querySelectorAll(query)`
Return a list of elements that matche a given CSS selector

Parameters
* **query** *(string)* - Specifies the CSS selector to be searched for 

Return type
* *list*

---

## HtmlElement API 

#### `HtmlElement.innerHTML(contents=None)`
Get and set the inner HTML contents of an element

Parameters
* **contents** *(string)* - If provided, specifies the new HTML content of the element

Return type
* *string*

---

#### `HtmlElement.textContent(contents=None)`
"Get and set the text content of an element

Parameters
* **contents** *(string)* - If provided, specifies the new text content of the element

Return type
* *string*

---

#### `HtmlElement.getAttribute(attribute)`
Get the value of the given attribute

Parameters
* **attribute** *(string)* - Specifies the element's attribute to return 

Return type
* *string*

---

#### `HtmlElement.setAttribute(attribute, value)`
Set the value of the given attribute

Parameters
* **attribute** *(string)* - Specifies the element's attribute to set 
* **value** *(string)* - Specifies new value of the specified attribute 

Return type
* *string*

---

#### `HtmlElement.tagName()`
Get the tag name of the element

Return type
* *string*

---

#### `HtmlElement.style(property, value=None)`
Get and set the value of the given CSS property

Parameters
* **property** *(string)* - Specifies the element's CSS property to set 
* **value** *(string)* - If provided, specifies new value of the specified property 

Return type
* *string*

---

#### `HtmlElement.parentElement()`
Get the element's parent element

Return type
* *HtmlElement*

---

#### `HtmlElement.children(deep=True)`
Get the element's children elements

Parameters
* **deep** *(boolean)* - If False, only return the element's direct children. If True, return all children. 

Return type
* *list*

---

#### `HtmlElement.remove()`
Delete the element

---

#### `HtmlElement.appendChild(children)`
Add the given children elements into the element

Parameters
* **children** *(list or HtmlElement)* - Specifies the element(s) to be added into the element 

---

#### `HtmlElement.insertBefore(children, before)`
Insert the given children elements into the element

Parameters
* **children** *(list or HtmlElement)* - Specifies the element(s) to be added into the element 
* **before** *(HtmlElement)* - Specifies the child element that the added elements should be placed before 

---
