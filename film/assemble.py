# blender -b --python assemble.py -- FRAMES_DIR SOUND.wav TITLE.png OUT.mp4 [title_seconds]
import bpy, sys, os
a = sys.argv[sys.argv.index('--') + 1:]
FR, SND, OVL, OUT = a[:4]; TS = float(a[4]) if len(a) > 4 else 2.8
sc = bpy.context.scene
sc.render.fps = 30; sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.sequencer_colorspace_settings.name = 'sRGB'
files = sorted(f for f in os.listdir(FR) if f.startswith('f') and f.endswith('.png'))
se = sc.sequence_editor_create()
col = getattr(se, 'strips', None) or se.sequences
st = col.new_image('frames', os.path.join(FR, files[0]), channel=1, frame_start=1)
for f in files[1:]: st.elements.append(f)
N = len(files); sc.frame_start = 1; sc.frame_end = N
col.new_sound('sound', SND, channel=2, frame_start=1)
T = int(TS * 30)
ov = col.new_image('title', OVL, channel=3, frame_start=N - T + 1)
ov.frame_final_duration = T; ov.blend_type = 'ALPHA_OVER'
ov.blend_alpha = 0.0; ov.keyframe_insert('blend_alpha', frame=N - T + 1)
ov.blend_alpha = 1.0; ov.keyframe_insert('blend_alpha', frame=N - T + 22)
r = sc.render; r.image_settings.file_format = 'FFMPEG'
r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'; r.ffmpeg.constant_rate_factor = 'HIGH'
r.ffmpeg.ffmpeg_preset = 'GOOD'; r.ffmpeg.audio_codec = 'AAC'; r.ffmpeg.audio_bitrate = 192; r.ffmpeg.audio_channels = 'STEREO'
r.filepath = OUT
bpy.ops.render.render(animation=True)
print('[film] wrote', OUT, N, 'frames', flush=True)
