#!/usr/bin/env python3

import concur as c
from PIL import Image
import numpy as np
import csv
import sys, os


def overlay(pts, tf):
    marker_r = 10
    while True:
        _, pos = yield from c.orr([
            c.draw.scatter(pts, 'black', '.', marker_r, tf=tf),
            c.draw.scatter(pts, 'green', '.', marker_r - 2, tf=tf),
            c.mouse_click("Click"),
            ])
        pts_s = tf.transform(pts)
        d = np.square(pos - pts_s).sum(axis=1)
        if len(d):
            pi = np.argmin(d)
            if marker_r ** 2 >= d[pi]:
                return "Rem", pi
        return "Add", np.dot(tf.s2c, [*pos, 1])


def app(image_path, output_path):
    view = c.Image(Image.open(image_path))
    autosave = True
    try:
        r = csv.reader(open(output_path, 'r'))
        pts = [(int(x), int(y)) for x, y in r]
    except FileNotFoundError:
        pts = []
    while True:
        tag, value = yield from c.orr([
            c.orr_same_line([c.button("Save"), c.text(f"Click to (de)annotate. N: {len(pts)}"), c.checkbox("Autosave", autosave)]),
            c.image("Image", view, content_gen=c.partial(overlay, np.array(pts).reshape(-1, 2))),
            ])
        if tag == "Image":
            view = value
        elif tag == "Autosave":
            autosave = value
        elif tag == "Rem":
            pts.pop(value)
        elif tag == "Add":
            pts.append((int(value[0]), int(value[1])))
        if tag == "Save" or autosave and tag in ["Rem", "Add"]:
            with open(output_path, 'w') as f:
                csv.writer(f).writerows(pts)
        yield


if __name__ == "__main__":
    if len(sys.argv) not in [2,3]:
        print("Usage:")
        print("    annotator.py <image> [output.csv]")
    else:
        input_path, output_path = sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else os.path.splitext(sys.argv[1])[0] + '.csv'
        c.main(app(input_path, output_path), "Annotator", 1280, 820)
