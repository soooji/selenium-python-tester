from itertools import groupby
import os
from utils import is_url_image, get_coordinates, rect_intersects
from consts import DEPRECATED_ATTRS

from selenium import webdriver

script_dir = os.path.dirname(__file__)


def get_full_path(rel_path):
    return os.path.join(script_dir, rel_path)


firefox_web_driver_path = get_full_path('geckodriver')
chrome_web_driver_path = get_full_path('chromedriver')

target_page_url = "http://kiswa.net/themes/kiswa/corporate/demo/demo-ltr/corporate-1.html"
first_html = "sample1.htm"
second_html = "sample2.htm"


def check_links_to_image(browser):
    links_are_image = [];
    links = browser.find_elements_by_css_selector('a')
    for link in links:
        l = link.get_attribute('href')
        if is_url_image(l):
            links_are_image.append({"el": link, "href": l})
    return links_are_image


def deprecated_attrs(browser):
    deprecated_elements = [];

    for row in DEPRECATED_ATTRS:
        for el in row[1]:
            element_types = browser.find_elements_by_css_selector(el)
            for item in element_types:
                if item.get_attribute(row[0]):
                    deprecated_elements.append({"el": item, "tag": el, "attr": row[0]})

    # Custom Exceptions
    script_tags = browser.find_elements_by_xpath("//script[@language]")
    for el in script_tags:
        if el.get_attribute('language').str.lower() != "javascript":
            deprecated_elements.append({"el": el, "tag": "script", "attr": "language"})

    a_tags = browser.find_elements_by_xpath("//a[@name and not(@name=@id)]")
    for el in a_tags:
        deprecated_elements.append({"el": el, "tag": "a", "attr": "name"})

    img_tags = browser.find_elements_by_xpath("//img[@border and not(@border=0)]")
    for el in img_tags:
        deprecated_elements.append({"el": el, "tag": "img", "attr": "border"})

    return deprecated_elements


def redirect_meta(browser):
    meta_tags = browser.find_elements_by_xpath("//meta[@http-equiv='refresh']")
    return meta_tags


def has_style_attr(browser):
    style_els = browser.find_elements_by_xpath("//*[@style]")
    return style_els


def links_with_same_text(browser):
    with_error_group_els = []

    els = browser.find_elements_by_xpath("//a[text()]")
    for k, same_text_group in groupby(els, lambda el: el.text):
        for j, same_link_group in groupby(same_text_group, lambda el: el.get_attribute('href')):
            to_list = list(same_link_group)
            if len(to_list) > 1:
                with_error_group_els.append(
                    {"text": to_list[0].text, "link": to_list[0].get_attribute('href'), "elements": to_list})

    return with_error_group_els


def check_overlapping(browser, rel_path):
    sizes = [[800, 600], [1024, 768], [1448, 1072], [1600, 1200], [2048, 1536]]
    browser.get("file://" + get_full_path(rel_path))
    browser.set_window_position(0, 0)
    res = {}
    for size in sizes:
        browser.set_window_size(size[0], size[1])
        size_key = str(size[0]) + "X" + str(size[1])
        res[size_key] = []
        al_els = []
        inputs = browser.find_elements_by_xpath("//input")
        al_els.extend(inputs)
        selects = browser.find_elements_by_xpath("//select")
        al_els.extend(selects)

        for i, el in enumerate(al_els):
            intersects_with_current = []
            for j, target_el in enumerate(al_els):
                if i != j:
                    if rect_intersects(get_coordinates(el), get_coordinates(target_el)):
                        intersects_with_current.append(target_el)

            res[size_key].append({"source_el": el, "intersect_with": intersects_with_current})

    return res


def new_crawler(i):
    browser = None

    if i == 'firefox':
        browser = webdriver.Firefox(executable_path=firefox_web_driver_path)
    else:
        browser = webdriver.Chrome(executable_path=chrome_web_driver_path)

    browser.get(target_page_url)

    link_to_images = check_links_to_image(browser)
    # print(link_to_images)

    deprecated_elements = deprecated_attrs(browser)
    # print(len(deprecated_elements))

    redirect_metas = redirect_meta(browser)
    # print(redirect_metas)

    has_inline_style = has_style_attr(browser)
    # print(has_inline_style)

    same_text_not_link = links_with_same_text(browser)
    # print(same_text_not_link)

    first_overlapping_res = check_overlapping(browser, first_html)
    # print(first_overlapping_res)

    second_overlapping_res = check_overlapping(browser, second_html)
    # print(second_overlapping_res)

    browser.close()
    return {'link_to_images': link_to_images, 'deprecated_elements': deprecated_elements,
            'redirect_metas': redirect_metas,
            'has_inline_style': has_inline_style, 'same_text_not_link': same_text_not_link,
            'first_overlapping_res': first_overlapping_res, 'second_overlapping_res': second_overlapping_res}


result_list = {'chrome': new_crawler('chrome'), 'firefox': new_crawler('firefox')}
print(result_list)
