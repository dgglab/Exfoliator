from motion_controller.mmc110 import MMC110


class Motor:
    mmc110: MMC110
    axis_number: int

    def __init__(self, mmc110: MMC110, axis_number: int):
        self.mmc110 = mmc110
        self.axis_number = axis_number
        self.mmc110.send(f'10MOT1')
        self.mmc110.send(f'{self.axis_number}MOT1')

    def step(self, step_size):
        self.mmc110.send(f'{self.axis_number}MVR{step_size}')


class EmulatedMotor(Motor):
    def step(self, step_size):
        print(f"Stepping motor by {step_size}")