#!/usr/bin/python3


class Target:
    """Target class is a data structure used in the RunStep class

        A target is either a percentage of the user's maximal heart rate, or a
        speed in km/h (not both at the same time). Runner will be told to run
        between at the corresponding target with a given margin.
    """
    # @TODO : use the prefix

    def __init__(self, hr=0, spd=0, margin=1., prefix=None):
        self.hr = hr
        self.spd = spd

        self.hrMin = hr - margin if hr else 0
        self.hrMax = hr + margin if hr else 0
        self.spdMin = spd - margin if spd else 0
        self.spdMax = spd + margin if spd else 0

        self.prefix = prefix


class Remaining:
    """Remaining class is a data structure used for the RunStep class

       It determines what is left to complete the current step in the training
       session, and move on to the next one. 'What is left' can be either a
       duration (in seconds), a distance (in km), or undefined. In the latter
       case, the next step only starts when the user pushes the 'lap'
       button. A prefix can be specified to give information on the current
       step, such as "warmup", or "cooldown".
    """

    def __init__(self, dur=0, dist=0, lap=False, prefix='"run"'):
        self.dur = dur
        self.dist = dist
        self.lap = lap

        self.prefix = prefix
        self.postfix = '"s"' if self.dur != 0 or self.lap else '"km"'


class RunStep:
    """RunStep class is used to represent a step where the user has to run

       There are two attributes: remaining for the first app, and target for
       the target app that can be None.
    """

    def __init__(self, remaining, target=None):
        self.remaining = remaining
        self.target = target

    def transitionCode(self, withBip=False):
        """return the code that is common to both remaining and target app. It
        is the code that will generate the transitions between the different
        steps"""

        out = ""
        if self.remaining.dur != 0:
            out += ("  if (SUUNTO_DURATION - last_step_duration >= " +
                    str(self.remaining.dur) + ") {\n")
        elif self.remaining.dist != 0:
            out += ("  if (SUUNTO_DISTANCE - last_step_distance >= " +
                    str(self.remaining.dist) + ") {\n")
        elif self.remaining.lap:
            out += "  if (SUUNTO_LAP_NUMBER > current_lap_number) {\n"
            out += "    current_lap_number = current_lap_number + 1;\n"

        out += "    last_step_duration = SUUNTO_DURATION;\n"
        out += "    last_step_distance = SUUNTO_DISTANCE;\n"
        if withBip:
            out += "    Suunto.alarmBeep();\n"
            out += "    Suunto.light();\n"
        out += "    step = step + 1;\n"
        out += "  }"

        return out

    def remainingApp(self):
        """return the code of the step for the remaining app"""

        out = ""

        out += "  prefix = " + self.remaining.prefix + ";\n"
        out += "  postfix = " + self.remaining.postfix + ";\n"

        if self.remaining.dur != 0:
            out += ("  RESULT = last_step_duration + " +
                    str(self.remaining.dur) + " - SUUNTO_DURATION;\n")
        elif self.remaining.dist != 0:
            out += ("  RESULT = last_step_distance + " +
                    str(self.remaining.dist) + " - SUUNTO_DISTANCE;\n")
        elif self.remaining.lap:
            out += "  RESULT = SUUNTO_LAP_DURATION;\n"

        out += self.transitionCode(withBip=True)

        return out

    def targetApp(self):
        """return the code of the step for the target app"""
        out = ""

        if self.target:
            if self.target.hrMax != 0:
                if not self.target.prefix:
                    self.target.prefix = '"HR"'
                out += '  prefix = ' + self.target.prefix + ';\n'
                out += "  RESULT = " + str(self.target.hr) + ";\n"
                out += ("  if (" + str(self.target.hrMax) +
                        " < (SUUNTO_HR *100 / " +
                        "SUUNTO_USER_MAX_HR)) {\n")
                out += '    postfix = "++";\n  }'
                out += ("  else if (" + str(self.target.hrMin) + " > " +
                        "(SUUNTO_HR * 100 / SUUNTO_USER_MAX_HR)) {\n")
                out += '    postfix = "--";\n  }'
                out += "  else {\n"
                out += '    postfix = "ok";\n  }\n'

            elif self.target.spdMax != 0:
                if not self.target.prefix:
                    self.target.prefix = '"spd"'
                out += '  prefix = ' + self.target.prefix + ';\n'
                out += "  RESULT = " + str(self.target.spd) + ";\n"
                out += ("  if (" + str(self.target.spdMax) +
                        " < SUUNTO_SPEED) {\n")
                out += '    postfix = "++";\n  }'
                out += ("  else if (" + str(self.target.spdMin) +
                        " > SUUNTO_SPEED) {\n")
                out += '    postfix = "--";\n  }'
                out += "  else {\n"
                out += '    postfix = "ok";\n  }\n'

        out += self.transitionCode()

        return out


class Repeat:
    """Repeat class used to represent repetition in a training program. Useful
    for interval training."""

    def __init__(self, nRepeat, runSteps):
        self.nRepeat = nRepeat  # number of repetitions
        self.runSteps = runSteps  # the list of Runsteps instances to repeat
        self.nSteps = len(self.runSteps)


def applicationCode(session, appType='remaining'):
    """ take a training session as input and return the code for the
    corresponding application. Application can be either 'remaining' or
    'target' """

    if appType == 'remaining':
        stepCode = lambda step: step.remainingApp()  # noqa
    else:
        stepCode = lambda step: step.targetApp()  # noqa

    out = ""
    stepi = 0

    for step in session:
        if isinstance(step, Repeat):
            for ssi, subStep in enumerate(step.runSteps):
                out += "if ("
                for n in range(0, step.nRepeat * step.nSteps, step.nSteps):
                    out += "step == " + str(stepi + ssi + n) + " || "
                out += "0){\n"
                out += stepCode(subStep)
                out += "\n}\n\n"
            stepi += step.nSteps * step.nRepeat

        else:
            out += "if (step == " + str(stepi) + ") {\n"
            out += stepCode(step)
            out += "\n}\n\n"
            stepi += 1

    return out
