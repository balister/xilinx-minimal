import enum
import time

import attr

from labgrid.factory import target_factory
from labgrid.step import step
from labgrid.strategy import Strategy, StrategyError
from labgrid.driver.usbstoragedriver import Mode
from labgrid.protocol import PowerProtocol, ConsoleProtocol
from labgrid.driver import ShellDriver, USBSDMuxDriver, USBStorageDriver

class Status(enum.Enum):
    unknown = 0
    off = 1
    flashed = 2
    shell = 3

@target_factory.reg_driver
@attr.s(eq=False)
class zcu104Strategy(Strategy):
    bindings = {
            "power": PowerProtocol,
            "console": ConsoleProtocol,
            "shell": ShellDriver,
            "sdmux": USBSDMuxDriver,
            "sdcard": USBStorageDriver,
        }

    status = attr.ib(default=Status.unknown)
    flashed = attr.ib(default=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    @step(args=["status"])
    def transition(self, status, *, step):
        if not isinstance(status, Status):
            status = Status[status]

        if status == Status.unknown:
            raise StrategyError(f"can not transition to {status}")

        elif status == self.status:
            step.skip("nothing to do")
            return

        elif status == Status.off:
            self.target.deactivate(self.shell)

            self.target.activate(self.power)
            self.power.off()

        elif status == Status.flashed:
            image = self.target.env.config.get_image_path("sd")

            self.transition(Status.off)

            # We only need to flash the iamge once, not for every test
            if not self.flashed:
                self.target.activate(self.sdmux)
                self.sdmux.set_mode("host")

                self.target.activate(self.sdcard)
                self.sdcard.write_image(image, Mode.BMAPTOOL)
                self.targte.deactivate(self.sdcard)

                self.sdmux.set_mode("dut")

                self.target.deactviate(self.sdmux)
    
                self.flashed = true

        elif status == Status.shell:
            self.transition(Status.flashed)

            self.power.on()
            time.sleep(5)

            self.target.activate(self.shell)

        else:
            raise StrategyError(f"no transition found from {self.status} to {status}")

        self.status = status

    def __del__(self):
        self.transition(Status.off)

