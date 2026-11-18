# Blender script: true elbow fold (180 - angle at the elbow between shoulder and wrist; 0 = straight) of the left arm,
# shoulder-line yaw and shoulder/elbow/wrist positions per drawing. usage: blender -b --factory-startup --python
# elbow_fold.py -- <path/to/sora_idle_loop.blend>
import sys, math, bpy
bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index('--') + 1])
s = bpy.context.scene; a = next(o for o in s.objects if o.type == 'ARMATURE'); P = a.pose.bones; M = a.matrix_world
for f in range(s.frame_start, s.frame_end + 1):
    s.frame_set(f)
    S, E, W = M @ P['L_ude1'].head, M @ P['L_ude2'].head, M @ P['L_te'].head
    bend = 180 - math.degrees((S - E).angle(W - E))
    L, R = M @ P['L_ude1'].head, M @ P['R_ude1'].head; d = L - R
    print('GEO', f, 'fold', round(bend, 1), 'yaw', round(math.degrees(math.atan2(d.y, d.x)), 1),
          'S', [round(c, 4) for c in S], 'E', [round(c, 4) for c in E], 'W', [round(c, 4) for c in W])
