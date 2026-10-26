"""Nominal dimensions in millimetres and revolute-joint angles in degrees."""
from itertools import product
from math import isfinite
from numbers import Real

HIP_X = (-62.5, -7.5)
HIP_Y = 48.0
HIP_Z = -20.0
HEAD_LIFT = 12.0
ANKLE_Y = 35.7
ANKLE_Z = -46.5
HIP_LIMIT_DEG = 20.0
ANKLE_LIMIT_DEG = 15.0
SERVO_LENGTH = 22.8
SERVO_WIDTH = 12.4
SERVO_CASE_DEPTH = 23.2
CLEARANCE = .35
OLED_PCB = (29.2, 26.7, 6.2)


def _positive_finite(value):
    return (isinstance(value, Real) and not isinstance(value, bool)
            and isfinite(value) and value > 0)


def validate(hip_limit=HIP_LIMIT_DEG, ankle_limit=ANKLE_LIMIT_DEG,
             servo_length=SERVO_LENGTH, servo_width=SERVO_WIDTH,
             servo_case_depth=SERVO_CASE_DEPTH, clearance=CLEARANCE,
             oled_pcb=OLED_PCB, head_lift=HEAD_LIFT):
    """Return validation errors; an empty tuple means the configuration is valid."""
    dimensions = (("servo_length", servo_length), ("servo_width", servo_width),
                  ("servo_case_depth", servo_case_depth), ("clearance", clearance),
                  ("head_lift", head_lift))
    errors = tuple(f"{name} must be finite and positive"
                   for name, value in dimensions if not _positive_finite(value))
    errors += tuple(f"{name} must be finite, positive, and at most 180 degrees"
                    for name, value in (("hip_limit", hip_limit), ("ankle_limit", ankle_limit))
                    if not _positive_finite(value) or value > 180)
    if (not isinstance(oled_pcb, (tuple, list)) or len(oled_pcb) != 3
            or not all(_positive_finite(value) for value in oled_pcb)):
        errors += ("oled_pcb must contain three finite positive dimensions",)
    return errors


def motion_samples(hip_limit=HIP_LIMIT_DEG, ankle_limit=ANKLE_LIMIT_DEG):
    """Return neutral, individual sweeps, then all joint-limit combinations.

    Tuple order is (hipL, hipR, ankleL, ankleR). These samples are collision
    checkpoints, not proof that every intermediate pose is collision-free.
    """
    errors = validate(hip_limit=hip_limit, ankle_limit=ankle_limit)
    if errors:
        raise ValueError("; ".join(errors))
    limits = (hip_limit, hip_limit, ankle_limit, ankle_limit)
    fractions = (-1, -.75, -.5, -.25, .25, .5, .75, 1)
    singles = tuple(tuple(limit * fraction if axis == index else 0.0
                          for axis in range(4))
                    for index, limit in enumerate(limits) for fraction in fractions)
    extremes = tuple(tuple(sign * limit for sign, limit in zip(signs, limits))
                     for signs in product((-1, 1), repeat=4))
    return tuple(dict.fromkeys(((0.0, 0.0, 0.0, 0.0),) + singles + extremes))
