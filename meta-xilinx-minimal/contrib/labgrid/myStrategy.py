import enum

import attr

from pexpect import TIMEOUT

from labgrid.factory import target_factory
from labgrid.strategy.common import Strategy, StrategyError

class Status(enum.Enum):
    unknown = 0
    off = 1
    uboot = 2
    shell = 3


@target_factory.reg_driver
@attr.s(eq=False)
class ZCU104Strategy(Strategy):
    """ZCU104Strategy - Strategy to bootstrap and switch to uboot or shell"""
    bindings = {
        "power": "PowerProtocol",
        "sdmux": "USBSDMuxDriver",
        "storage": "USBStorageDriver",
        "console": "ConsoleProtocol",
        "uboot": "UBootDriver",
        "shell": "ShellDriver",
    }

    status = attr.ib(default=Status.unknown)
    flashed = False

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    def bootstrap(self):
        self.target.activate(self.sdmux)
        self.sdmux.set_mode("host")
 
        if not self.flashed:
            self.target.activate(self.storage)
            image = self.target.env.config.get_image_path("sd_image")

            self.storage.write_image(image)
            self.target.deactivate(self.storage)
            self.flashed = True

        self.sdmux.set_mode("dut")

    def transition(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"can not transition to {status}")
        elif status == self.status:
            return # nothing to do
        elif status == Status.off:
            self.target.deactivate(self.console)
            self.target.activate(self.power)
            self.power.off()
        elif status == Status.uboot:
            self.transition(Status.off)

            self.bootstrap()

            self.target.activate(self.console)
            # cycle power
            timeout_count = 0
            while True:
                try:
                    self.power.cycle()
                    # interrupt uboot
                    self.target.activate(self.uboot)
                    break
                except TIMEOUT:
                    timeout_count += 1
                    if timeout_count == 3:
                        raise
        elif status == Status.shell:
            # transition to uboot
            self.transition(Status.uboot)
            self.uboot.boot("")
            self.uboot.await_boot()
            self.target.activate(self.shell)
            self.shell.run("systemctl is-system-running --wait")
        else:
            raise StrategyError(f"no transition found from {self.status} to {status}")
        self.status = status

    def force(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.off:
            self.target.activate(self.power)
        elif status == Status.uboot:
            self.target.activate(self.uboot)
        elif status == Status.shell:
            self.target.activate(self.shell)
        else:
            raise StrategyError(f"can not force state {status}")
        self.status = status
