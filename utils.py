import mimetypes


def is_url_image(url):
    mimetype, encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))


def get_coordinates(el):
    location = el.location
    size = el.size
    w, h = size['width'], size['height']

    x1, y1 = location['x'], location['y']
    top_left = {'x': x1, 'y': y1}
    top_right = {'x': x1 + w, 'y': y1}

    bottom_left = {'x': x1, 'y': y1 + h}
    bottom_right = {'x': x1 + w, 'y': y1 + h}

    return {'top_left': top_left, 'top_right': top_right, 'bottom_left': bottom_left, 'bottom_right': bottom_right}


def rect_intersects(first, second):
    return not (
            first['top_right']['x'] < second['bottom_left']['x'] or first['bottom_left']['x'] > second['top_right'][
        'x'] or first['top_right']['y'] > second['bottom_left']['y'] or first['bottom_left']['y'] < second['top_right'][
                'y'])
