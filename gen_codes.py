from string import Template
from typing import Iterable, List, Tuple
import ffmpeg
import cairosvg
from pathlib import Path


def render_code(code: str):
    code_template = Template(open("code_template.svg", "r").read())
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    out_path = tmp_dir / f"{code}.png"
    cairosvg.svg2png(
        bytestring=code_template.substitute({"code": code}), write_to=str(out_path)
    )
    return out_path


def run_overwriting(x, output: Path):
    ffmpeg.run(ffmpeg.output(x, str(output)).overwrite_output())


def collate_clips(frame_directory: str, transitions: List[int]) -> Iterable[Path]:
    logo = ffmpeg.input(
        f"resources/{frame_directory}/*.png",
        pattern_type="glob",
        framerate=25,
    )
    clips = [
        ffmpeg.trim(logo, start_frame=a, end_frame=b)
        if b is not None
        else ffmpeg.trim(logo, start_frame=a)
        for (a, b) in zip([0] + transitions, transitions + [None])
    ]
    for (idx, clip) in enumerate(clips):
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)
        path = tmp_dir / f"{frame_directory}_{idx}.webm"
        if not path.exists():
            run_overwriting(clip, path)
        yield path


def render_animation(clips: List[Path], code: str, path: Path):
    code_overlay = render_code(code)
    input_streams = [ffmpeg.input(str(path)) for path in clips]
    run_overwriting(
        ffmpeg.concat(
            input_streams[0],
            ffmpeg.overlay(
                input_streams[1],
                ffmpeg.input(code_overlay),
            ),
            input_streams[2],
        ),
        path,
    )


if __name__ == "__main__":
    clips = list(collate_clips("german_frames", [150, 209]))
    dir = Path("output/german")
    dir.mkdir(exist_ok=True, parents=True)
    for code in open("codes/german_codes", "r").readlines():
        code = code.strip()
        render_animation(clips, code, dir / f"{code}.webm")
