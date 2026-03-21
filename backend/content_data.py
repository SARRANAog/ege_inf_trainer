"""Content data aggregator for theory, exercises and roadmap."""

try:
    from .theory_content import THEORY_DATA
    from .exercises_content import EXERCISES_DATA as BASE_EXERCISES
    from .exercises_extra import EXTRA_EXERCISES
    from .exercises_extra_2 import EXTRA_EXERCISES_2
    from .roadmap_content import ROADMAP_DATA
except ImportError:
    from theory_content import THEORY_DATA
    from exercises_content import EXERCISES_DATA as BASE_EXERCISES
    from exercises_extra import EXTRA_EXERCISES
    from exercises_extra_2 import EXTRA_EXERCISES_2
    from roadmap_content import ROADMAP_DATA

EXERCISES_DATA = BASE_EXERCISES + EXTRA_EXERCISES + EXTRA_EXERCISES_2

__all__ = ["THEORY_DATA", "EXERCISES_DATA", "ROADMAP_DATA"]
