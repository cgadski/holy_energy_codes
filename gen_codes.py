# %%
from string import Template
import ffmpeg
import imgkit


#%%
code_template = Template(open("code_template.html", "r").read())

def render_code(code: str):
    fp = f"tmp/code_{code}.png"
    imgkit.from_string(
        code_template.substitute({"code": code}),
        fp,
        options={
            "transparent": None,
            "width": 500,
            "height": 320,
        },
    )
    return fp

render_code("hello")

# %%
def put_code(stream, code: str):
    overlay = ffmpeg.input(render_code(code))
    return ffmpeg.overlay(
        stream,
        overlay 
    )


def run(x):
    ffmpeg.run(x.overwrite_output())

# %%
logo = ffmpeg.input("resources/frames/*.png", pattern_type="glob", framerate=25)
start_frames = 102
logo_before = ffmpeg.trim(logo, start_frame=0, end_frame=start_frames)
logo_after = ffmpeg.trim(logo, start_frame=start_frames)
ffmpeg.run(ffmpeg.output(logo_before, "output/before.webm").overwrite_output())
ffmpeg.run(ffmpeg.output(logo_after, "output/after.webm").overwrite_output())
logo_before = ffmpeg.input("output/before.webm")
logo_after = ffmpeg.input("output/after.webm")


# %%
for code in open("codes", "r").readlines():
    code = code.strip()
    code_output = ffmpeg.concat(logo_before, put_code(logo_after, code))
    run(code_output.output(f"output/{code}.webm", gifflags=None, offsetting=None).overwrite_output())

# %%
