"""
アトリエとなりの — メディア準備スクリプト（Python 3.12）

  サムネ → WebP（長辺640px）、動画 → ウェブ用 MP4（長辺720px・音声なし）に変換して
  media/works/<id>/ や media/log/ に決まった名前で置きます。

必要なもの:
  pip install pillow
  ffmpeg（PATH が通っていること。動画を扱うときだけ）

使い方（どこから実行しても、このスクリプトの1つ上のフォルダ＝リポジトリ直下が基準）:
  旧ギャラリーからの一括移行（最初の1回だけ）
    python tools/media.py migrate --src ../TonarinoShaderGallery

  作品を1つ追加
    python tools/media.py add new-work --thumb D:/rec/new.png --video D:/rec/new.mp4
    python tools/media.py add still-work --thumb D:/rec/still.png --image D:/rec/still.png

  実験ログのスクショを追加（media/log/<id>.webp）
    python tools/media.py log 2026-winter --image D:/shots/booth.png
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
WORKS = ROOT / "media" / "works"
LOG = ROOT / "media" / "log"

THUMB_SIZE = 640
LOG_WIDTH = 960
VIDEO_MAX = 720
VIDEO_CRF = "28"

# 旧 themes/ のフォルダ名 → 新しい id
LEGACY = {
    "ArchimedeanSolidPlanet": "archimedean-solid-planet",
    "FloatingGoldfish": "floating-goldfish",
    "FuwaFuwaHalloweenGhost": "fuwafuwa-halloween-ghost",
    "JetEngine": "jet-engine",
    "JumpingSquares": "jumping-squares",
    "MarchingKadomatsu": "marching-kadomatsu",
    "MorphingPonde": "morphing-ponde",
    "RainbowCircle": "rainbow-circle",
    "RainbowCogwheel": "rainbow-cogwheel",
    "SpaceJellyfish": "space-jellyfish",
    "SquareCarpet": "square-carpet",
    "SymbolSoda": "symbol-soda",
    "TruchetCirkit": "truchet-cirkit",
    "VoronoiCrystal": "voronoi-crystal",
}


def save_webp(src: Path, dst: Path, *, box: int | None = None, width: int | None = None) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        if box:
            im.thumbnail((box, box), Image.LANCZOS)
        elif width and im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=82, method=6)
    print(f"  画像  {rel(dst)}  ({dst.stat().st_size // 1024} KB)")


def encode_video(src: Path, dst: Path, *, copy: bool = False) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if copy:
        shutil.copy2(src, dst)
        print(f"  動画  {rel(dst)}  (無変換コピー)")
        return
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg が見つかりません。インストールするか --copy-video を付けてください。")
    scale = (f"scale={VIDEO_MAX}:{VIDEO_MAX}:force_original_aspect_ratio=decrease,"
             "scale=trunc(iw/2)*2:trunc(ih/2)*2")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
           "-an", "-vf", scale,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", VIDEO_CRF,
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)]
    subprocess.run(cmd, check=True)
    before = src.stat().st_size / 1_048_576
    after = dst.stat().st_size / 1_048_576
    print(f"  動画  {rel(dst)}  ({before:.1f} MB → {after:.1f} MB)")


def rel(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def add_work(work_id: str, thumb: Path, video: Path | None, image: Path | None, copy_video: bool) -> None:
    out = WORKS / work_id
    print(f"[{work_id}]")
    save_webp(thumb, out / "thumb.webp", box=THUMB_SIZE)
    if image:
        out.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, out / "image.png")
        print(f"  原寸  {rel(out / 'image.png')}")
    if video:
        encode_video(video, out / "video.mp4", copy=copy_video)


def cmd_migrate(args: argparse.Namespace) -> None:
    themes = Path(args.src).resolve() / "themes"
    if not themes.is_dir():
        sys.exit(f"themes フォルダが見つかりません: {themes}")
    for folder in sorted(p for p in themes.iterdir() if p.is_dir()):
        work_id = LEGACY.get(folder.name)
        if not work_id:
            print(f"[skip] 対応表にないフォルダ: {folder.name}")
            continue
        pngs = sorted(folder.rglob("*.png"))
        mp4s = sorted(folder.rglob("*.mp4"))
        if not pngs:
            print(f"[skip] 画像がない: {folder.name}")
            continue
        image = pngs[0] if not mp4s else None
        add_work(work_id, pngs[0], mp4s[0] if mp4s else None, image, args.copy_video)
    print("完了。data/works.json の id と一致しているか確認してください。")


def cmd_add(args: argparse.Namespace) -> None:
    add_work(args.id, Path(args.thumb), Path(args.video) if args.video else None,
             Path(args.image) if args.image else None, args.copy_video)


def cmd_log(args: argparse.Namespace) -> None:
    save_webp(Path(args.image), LOG / f"{args.id}.webp", width=LOG_WIDTH)
    print(f'data/log.json の該当項目に "image": true を足してください。')


def main() -> None:
    ap = argparse.ArgumentParser(description="アトリエとなりの メディア準備")
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("migrate", help="旧 TonarinoShaderGallery の themes/ を一括移行")
    m.add_argument("--src", required=True, help="旧リポジトリのフォルダ")
    m.add_argument("--copy-video", action="store_true", help="動画を圧縮せずそのままコピー")
    m.set_defaults(func=cmd_migrate)

    a = sub.add_parser("add", help="作品を1つ追加")
    a.add_argument("id", help="フォルダ名（小文字とハイフン）例: space-jellyfish")
    a.add_argument("--thumb", required=True, help="サムネの元画像")
    a.add_argument("--video", help="動画（あれば）")
    a.add_argument("--image", help="原寸画像（静止画の作品のとき）")
    a.add_argument("--copy-video", action="store_true", help="動画を圧縮せずそのままコピー")
    a.set_defaults(func=cmd_add)

    lg = sub.add_parser("log", help="実験ログのスクショを追加")
    lg.add_argument("id", help="log.json の id 例: 2026-winter")
    lg.add_argument("--image", required=True, help="スクショ")
    lg.set_defaults(func=cmd_log)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
