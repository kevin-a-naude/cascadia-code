# This code is not intended for general use.
#
# It is a simple script for generating small-cap glyphs for uppercase characters
# that do not yet have then. It also generates some fragment content for
# integrating into other files of the UFO format.

from fontTools.misc.filenames import userNameToFileName
import os
from pathlib import Path
import ufoLib2


Y_SCALE_PRECISION = 8


def formatScale(yScale, precision = Y_SCALE_PRECISION):
    if precision > 0:
        return f"{{:0.{precision}f}}".format(yScale)
    else:
        return f"{yScale}"


def generate_single_small_cap(path, glyphName, scGlyphName, yScale):
    yScaleFormatted = formatScale(yScale)
    with open(path, "w") as f:
        output = "\n".join([
            "<?xml version='1.0' encoding='UTF-8'?>",
            f"<glyph name=\"{scGlyphName}\" format=\"2\">",
            "  <advance width=\"1200\"/>",
            "  <outline>",
            f"    <component base=\"{glyphName}\" yScale=\"{yScaleFormatted}\" />",
            "  </outline>",
            "</glyph>",
            ""
        ])
        f.write(output)


def generate_missing_small_caps(input_dir, instance_descriptor):
    uppercaseGlyphs = []
    uppercaseGlyphsFound = dict()
    allContentLines = []
    newContentLines = []

    path = instance_descriptor.path.replace("instance_ufos/", "")
    glyphsPath = Path(path) / "glyphs"
    newBasePath = Path(path) / "missing-sc"
    newGlyphsPath = newBasePath / "glyphs"

    font = ufoLib2.Font.open(path)

    yScale = font.info.xHeight / font.info.capHeight
    yScaleFormatted = formatScale(yScale)

    print(f"Generating missing small caps: {path}")
    print("See extra-glyphs.txt and extra-glyphs-content.txt for results")
    print(f"font.info.capHeight = {font.info.capHeight}")
    print(f"font.info.xHeight = {font.info.xHeight}")
    print(f"yScale = {yScale}, rounded to {yScaleFormatted}")

    for glyphName in font.glyphOrder:
        glyph = font[glyphName]
        isUpperCase = any(chr(unicode).isupper() for unicode in glyph.unicodes)
        if isUpperCase:
            uppercaseGlyphs.append(glyphName)

            glyphFileName = userNameToFileName(glyphName, suffix=".glif")
            glyphFilePath = glyphsPath / glyphFileName
            uppercaseGlyphsFound[glyphName] = glyphFilePath.is_file()
            allContentLines.append(f"    <key>{glyphName}</key>")
            allContentLines.append(f"    <string>{glyphFileName}</string>")

            scGlyphName = glyphName + ".sc"
            glyphFileName = userNameToFileName(scGlyphName, suffix=".glif")
            glyphFilePath = glyphsPath / glyphFileName
            uppercaseGlyphsFound[scGlyphName] = glyphFilePath.is_file()
            allContentLines.append(f"    <key>{scGlyphName}</key>")
            allContentLines.append(f"    <string>{glyphFileName}</string>")

            if not uppercaseGlyphsFound[scGlyphName]:
                print(f"Generating small cap for {glyph.name}")
                if not newBasePath.is_dir():
                    os.mkdir(newBasePath)
                if not newGlyphsPath.is_dir():
                    os.mkdir(newGlyphsPath)
                glyphFilePath = newGlyphsPath / userNameToFileName(scGlyphName, suffix=".glif")
                generate_single_small_cap(glyphFilePath, glyphName, scGlyphName, yScale)
                newContentLines.append(f"    <key>{scGlyphName}</key>")
                newContentLines.append(f"    <string>{glyphFileName}</string>")
    if (len(newContentLines) > 0):
        with open(newBasePath / "uppercase.txt", "w") as f:
            output = " ".join(uppercaseGlyphs)
            f.write("@Uppercase = [ " + output + " ]\n\n")
            output = " ".join([glyph + ".sc" for glyph in uppercaseGlyphs])
            f.write("@Uppercase.sc = [ " + output + " ]\n")
        with open(newBasePath / "contents.plist-fragment.all.txt", "w") as f:
            output = "\n".join(allContentLines)
            f.write(output)
        with open(newBasePath / "contents.plist-fragment.new.txt", "w") as f:
            output = "\n".join(newContentLines)
            f.write(output)
    else:
        print(f"No extra small caps needed for font: {path}")
