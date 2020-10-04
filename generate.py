from fontTools.misc.filenames import userNameToFileName
from pathlib import Path
import ufoLib2


Y_SCALE_PRECISION = 8


def formatScale(yScale, precision = Y_SCALE_PRECISION):
    if precision > 0:
        return f"{{:0.{precision}f}}".format(yScale)
    else:
        return f"{yScale}"


def generate_single_small_cap(path, mainGlyphName, scGlyphName, yScale):
    yScaleFormatted = formatScale(yScale)
    with open(path, "w") as f:
        output = "\n".join([
            "<?xml version='1.0' encoding='UTF-8'?>",
            f"<glyph name=\"{scGlyphName}\" format=\"2\">",
            "  <advance width=\"1200\"/>",
            "  <outline>",
            f"    <component base=\"{mainGlyphName}\" yScale=\"{yScaleFormatted}\" />",
            "  </outline>",
            "</glyph>",
            ""
        ])
        f.write(output)


def generate_missing_small_caps(input_dir, instance_descriptor):
    extraGlyphs = []
    extraGlyphsContent = []
    path = instance_descriptor.path.replace("instance_ufos/", "")
    glyphsPath = Path(path) / "glyphs"
    font = ufoLib2.Font.open(path)
    yScale = font.info.xHeight / font.info.capHeight
    yScaleFormatted = formatScale(yScale)
    print(f"Generating missing small caps: {path}")
    print("See extra-glyphs.txt and extra-glyphs-content.txt for results")
    print(f"font.info.capHeight = {font.info.capHeight}")
    print(f"font.info.xHeight = {font.info.xHeight}")
    print(f"yScale = {yScale}, rounded to {yScaleFormatted}")
    for mainGlyphName in font.glyphOrder:
        glyph = font[mainGlyphName]
        isUpperCase = any(chr(unicode).isupper() for unicode in glyph.unicodes)
        if isUpperCase:
            scGlyphName = mainGlyphName + ".sc"
            scGlyphFileName = userNameToFileName(scGlyphName, suffix=".glif")
            glyphFile = glyphsPath / scGlyphFileName
            if not (glyphFile.is_file()):
                print(f"Generating small cap for {glyph.name}")
                generate_single_small_cap(glyphFile, mainGlyphName, scGlyphName, yScale)
                extraGlyphs.append(f"      <string>{scGlyphName}</string>")
                extraGlyphsContent.append(f"    <key>{scGlyphName}</key>")
                extraGlyphsContent.append(f"    <string>{scGlyphFileName}</string>")
    if len(extraGlyphs) > 0:
        with open(input_dir / "extra-glyphs.txt", "w") as f:
            output = "\n".join(extraGlyphs)
            f.write(output)
    if len(extraGlyphsContent) > 0:
        with open(input_dir / "extra-glyphs-content.txt", "w") as f:
            output = "\n".join(extraGlyphsContent)
            f.write(output)
    if len(extraGlyphs) == 0 and len(extraGlyphsContent) == 0:
        print(f"No extra small caps needed for font: {path}")
