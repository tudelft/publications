#!/usr/bin/env python


def bib_tag( line):
    return line.split("=", 1)[0].strip()

def bib_tag_content( line):
    return line.split("=", 1)[-1].strip().lstrip("=").rstrip(",").strip().lstrip("\"").rstrip("\"").lstrip("{").rstrip("}").strip()


with open("mavlab.bib") as ft:
    bibfile = ft.read().splitlines()

if __name__ == '__main__':
    with open("mavlab2.bib","w") as f:
        for line in bibfile:
            if "=" in line:
                tag = bib_tag( line ).lower()
                f.write("\t" + tag+" = {" + bib_tag_content(line) + "},\n")
            else:
                f.write(line+"\n")


