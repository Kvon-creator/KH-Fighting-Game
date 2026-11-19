"""Where each of Sora's version folders lives (Kvon, November 18: "organize all the folders in Sora's folder into
folders that correlate to the feature/animation that is being referenced").

The scripts keep writing `SORA / '<version folder>'` (or `SORA / '<version folder>/<file>'`): this SORA puts a version
folder under its feature group, picked from the name's start - e.g. 'atk_cmed2d_v24' ->
design/models/sora/attacks/crouching_medium/atk_cmed2d_v24. A name with no group (downloads, blender_workflow, a new
kind of folder) stays at design/models/sora/<name>. New builds land in their group automatically.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'design/models/sora'

# First match wins: the grabs before the general hurt_ / atk_ groups, jump_bdash / jump_dash / jump_spin before jump_.
GROUPS = [
    (('atk_agrab', 'hurt_agrab'), 'grabs/air_grab'),
    (('atk_grab', 'hurt_grab'), 'grabs/ground_grab'),
    (('atk_slight',), 'attacks/standing_light'),
    (('atk_smed',), 'attacks/standing_medium'),
    (('atk_sheavy',), 'attacks/standing_heavy'),
    (('atk_clight',), 'attacks/crouching_light'),
    (('atk_cmed',), 'attacks/crouching_medium'),
    (('atk_cheavy',), 'attacks/crouching_heavy'),
    (('atk_jlight',), 'attacks/jumping_light'),
    (('atk_jmed',), 'attacks/jumping_medium'),
    (('atk_jheavy',), 'attacks/jumping_heavy'),
    (('saved_attacks',), 'attacks'),
    (('atk_guard',), 'guard'),
    (('qrun_', 'atk_qrm', 'atk_qrh'), 'specials/quick_run'),
    (('hurt_',), 'hurt'),
    (('jump_bdash',), 'movement/back_dash'),
    (('jump_dash',), 'movement/air_dash'),
    (('jump_spin',), 'movement/double_jump'),
    (('jump_',), 'movement/jump'),
    (('glide_',), 'movement/glide'),
    (('crouch_',), 'movement/crouch'),
    (('shuffle',), 'movement/walk_shuffle'),
    (('battle_v', 'sprite2d_v'), 'idle'),
    (('character_blockout_',), 'model/from_scratch_blockout'),
    (('boxes_preview',), 'combat'),
    (('gemini_animation', 'gemini_walk_review', 'momask_trial', 'pose_edit'), 'research'),
]


def group_of(name):
    """The feature group folder (relative to design/models/sora) for a version folder name, or '' for none."""
    for starts, group in GROUPS:
        if name.startswith(starts):
            return group
    return ''


class _SoraDir:
    """design/models/sora, but `/ 'name...'` goes through the name's feature group."""

    def __truediv__(self, rel):
        rel = str(rel).replace('\\', '/')
        group = group_of(rel.split('/', 1)[0])
        return BASE / group / rel if group else BASE / rel

    def __fspath__(self):
        return str(BASE)

    def __str__(self):
        return str(BASE)


SORA = _SoraDir()


if __name__ == '__main__':
    # self-check: every version folder sits where SORA says it is
    import sys
    bad = []
    for d in sorted(p for p in BASE.rglob('*') if p.is_dir() and (p / 'Idle_Loop_Report.json').exists()
                    and 'saved_attacks' not in p.parts):   # saved alternates: an archive, not looked up by name
        if SORA / d.name != d:
            bad.append(f'{d.relative_to(BASE)} -> expected {(SORA / d.name).relative_to(BASE)}')
    print('\n'.join(bad) or 'SORA_PATHS_OK')
    sys.exit(1 if bad else 0)
