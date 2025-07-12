# CAP Widget Django Template Tags

This document explains how to use the custom Django template tags for the CAP widget.

## Installation

Make sure the `django_cap` app is included in your `INSTALLED_APPS` in Django settings.

## Usage

### 1. Load the template tags

At the top of your template, load the django_cap template tags:

```django
{% load django_cap %}
```

### 2. Include the widget script

In the `<head>` section of your HTML, include the CAP widget script:

```django
{% cap_widget_script %}
```

This will output:
```html
<script src="https://cdn.jsdelivr.net/npm/@cap.js/widget@0.1.25" async></script>
```

The script URL can be configured via the `CAP_WIDGET_URL` Django setting.

### 3. Insert CAP widgets

#### Basic widget

```django
{% cap_widget %}
```

This creates a basic CAP widget with default settings:
```html
<cap-widget id="cap" data-cap-api-endpoint="/cap/v1/"></cap-widget>
```

#### Widget with custom parameters

```django
{% cap_widget widget_id="my-cap" api_endpoint="/custom/endpoint/" %}
```

#### Widget with built-in event handler

```django
{% cap_widget widget_id="cap-with-handler" with_handler=True %}
```

This includes a basic JavaScript event handler that logs the token to the console.

#### Widget with custom handler function

```django
{% cap_widget_with_handler widget_id="cap-custom" handler_function="myHandler" %}
```

Then define your custom handler function in JavaScript:

```javascript
function myHandler(token, event) {
    // Your custom logic here
    console.log("Token received:", token);
}
```

## Template Tag Reference

### `{% cap_widget_script %}`

Includes the CAP widget JavaScript library.

**Parameters:** None

### `{% cap_widget %}`

Inserts a CAP widget element.

**Parameters:**
- `widget_id` (optional): The HTML ID for the widget element. Default: "cap"
- `api_endpoint` (optional): The API endpoint for the widget. Default: "/cap/v1/"
- `with_handler` (optional): If True, includes a basic event handler. Default: False

### `{% cap_widget_with_handler %}`

Inserts a CAP widget with a custom JavaScript handler function.

**Parameters:**
- `widget_id` (optional): The HTML ID for the widget element. Default: "cap"
- `api_endpoint` (optional): The API endpoint for the widget. Default: "/cap/v1/"
- `handler_function` (optional): Name of the JavaScript function to call when solved. Default: "handleCapSolve"

## Configuration

You can configure the widget behavior via Django settings:

```python
# The URL for the CAP widget JavaScript library
CAP_WIDGET_URL = "https://cdn.jsdelivr.net/npm/@cap.js/widget@0.1.25"
```

## Complete Example

```django
{% load django_cap %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Page</title>

    {% cap_widget_script %}
</head>
<body>
    <h1>Contact Form</h1>

    <form method="post">
        {% csrf_token %}
        <!-- Your form fields here -->

        <!-- CAP widget for verification -->
        {% cap_widget widget_id="contact-form-cap" with_handler=True %}

        <button type="submit">Submit</button>
    </form>
</body>
</html>
```
