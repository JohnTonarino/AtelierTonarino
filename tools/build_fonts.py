"""
アトリエとなりの — フォント間引きスクリプト（Python 3.12）

日本語フォントは1本数MBあるので、サイトで実際に使っている文字だけを残した
WOFF2 を assets/fonts/ に書き出します。ここにない文字はシステムフォントで表示されます。

準備:
  pip install fonttools brotli
  Google Fonts から次の3ファミリーをダウンロードし、中の .ttf を tools/fonts-src/ に置く。
  ライセンス文はファミリーごとに著作権表記が違うので、zip 内の OFL.txt を
  OFL-DelaGothicOne.txt / OFL-ZenMaruGothic.txt / OFL-Yomogi.txt に名前を変えて同じ場所へ。
  （tools/fonts-src/ は .gitignore 済み）
    - Dela Gothic One   → DelaGothicOne-Regular.ttf
    - Zen Maru Gothic   → ZenMaruGothic-Medium.ttf / -Bold.ttf / -Black.ttf
    - Yomogi            → Yomogi-Regular.ttf

実行（作品やログで新しい漢字が増えたらもう一度）:
  python tools/build_fonts.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "fonts-src"
OUT = ROOT / "assets" / "fonts"

FONTS = [
    "DelaGothicOne-Regular",
    "ZenMaruGothic-Medium",
    "ZenMaruGothic-Bold",
    "ZenMaruGothic-Black",
    "Yomogi-Regular",
]

# いつでも入れておく文字: ASCII、ひらがな、カタカナ、よく使う記号、全角英数
BASE = "".join(chr(c) for c in range(0x20, 0x7F))
BASE += "".join(chr(c) for c in range(0x3040, 0x30A0))   # ひらがな
BASE += "".join(chr(c) for c in range(0x30A0, 0x3100))   # カタカナ
BASE += "".join(chr(c) for c in range(0xFF01, 0xFF5F))   # 全角英数・記号
BASE += "、。・ー〜「」『』（）【】！？…‥―→←↑↓○●◎★☆♪©"


def site_text() -> str:
    parts = [(ROOT / "index.html").read_text(encoding="utf-8")]
    parts += [p.read_text(encoding="utf-8") for p in sorted((ROOT / "data").glob("*.json"))]
    return "".join(parts)


def main() -> None:
    if not SRC.is_dir():
        sys.exit(f"{SRC} がありません。Google Fonts の .ttf を置いてください。")
    chars = sorted(set(BASE + site_text()) - set("\n\r\t"))
    text = "".join(chars)
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"対象文字数: {len(chars)}")

    for name in FONTS:
        src = SRC / f"{name}.ttf"
        if not src.exists():
            print(f"[skip] 見つからない: {src.name}")
            continue
        dst = OUT / f"{name}.woff2"
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.name_languages = ["*"]
        opts.notdef_outline = True
        font = subset.load_font(str(src), opts)
        sub = subset.Subsetter(opts)
        sub.populate(text=text)
        sub.subset(font)
        subset.save_font(font, str(dst), opts)
        print(f"  {dst.name}: {src.stat().st_size // 1024} KB → {dst.stat().st_size // 1024} KB")

    licenses = sorted(SRC.glob("OFL*.txt"))
    for lic in licenses:
        shutil.copy2(lic, OUT / lic.name)
        print(f"  {lic.name} をコピーしました")
    if len(licenses) < 3:
        print("[注意] ライセンス文が3つ揃っていません。OFL-DelaGothicOne.txt / OFL-ZenMaruGothic.txt / OFL-Yomogi.txt を tools/fonts-src/ に置いてください。")


if __name__ == "__main__":
    main()
