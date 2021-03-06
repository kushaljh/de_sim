""" Test utilities

:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Date: 2018-02-26
:Copyright: 2018-2020, Karr Lab
:License: MIT
"""

from abc import ABCMeta, abstractmethod
from capturer import CaptureOutput
from logging2 import Logger, LogLevel, StdOutHandler
import sys
import unittest

from de_sim.utilities import ConcreteABCMeta, SimulationProgressBar, FastLogger
from de_sim.config import core
from wc_utils.debug_logs.core import DebugLogsManager


class AbstractBase(object, metaclass=ABCMeta):

    @abstractmethod
    def f(self):
        raise NotImplementedError()

    @abstractmethod
    def g(self):
        raise NotImplementedError()


class YourMeta(type):
    def __new__(cls, *args, **kwargs):
        newcls = super().__new__(cls, *args, **kwargs)
        return newcls


class CombinedMeta(ConcreteABCMeta, YourMeta):
    pass


class TestConcreteClass(unittest.TestCase):

    def test(self):
        with self.assertRaisesRegex(TypeError, "ConcreteClass has not implemented abstract methods"):
            class ConcreteClass(AbstractBase, metaclass=CombinedMeta):
                pass


class TestSimulationProgressBar(unittest.TestCase):

    def test_progress(self):
        unused_bar = SimulationProgressBar()
        self.assertEqual(unused_bar.start(1), None)
        self.assertEqual(unused_bar.progress(2), None)
        self.assertEqual(unused_bar.end(), None)

        used_bar = SimulationProgressBar(True)
        with CaptureOutput(relay=True) as capturer:
            try:
                duration = 20
                self.assertEqual(used_bar.start(duration), None)
                self.assertEqual(used_bar.progress(10), None)
                # view intermediate progress
                print('', file=sys.stderr)
                self.assertEqual(used_bar.progress(20), None)
                self.assertEqual(used_bar.end(), None)
                self.assertTrue("/{}".format(duration) in capturer.get_text())
                self.assertTrue("max_time".format(duration) in capturer.get_text())

            except ValueError as e:
                if str(e) == 'I/O operation on closed file':
                    pass
                    # This ValueError is raised because progressbar expects sys.stderr to remain open
                    # for an extended time period but karr_lab_build_utils run-tests has closed it.
                    # Since SimulationProgressBar works and passes tests under naked pytest, and
                    # progressbar does not want to address the conflict over sys.stderr
                    # (see https://github.com/WoLpH/python-progressbar/issues/202) we let this
                    # test fail under karr_lab_build_utils.
                else:
                    self.fail('test_progress failed for unknown reason')


class TestFastLogger(unittest.TestCase):

    def setUp(self):
        self.fixture_level = LogLevel.warning
        fixture_handler = StdOutHandler(name="handler_fixture", level=self.fixture_level)
        self.fixture_logger = Logger("logger_fixture", handler=fixture_handler)

    def test_active_logger(self):
        for log_level in LogLevel:
            active = FastLogger.active_logger(self.fixture_logger, log_level.name)
            self.assertEqual(active, self.fixture_level <= log_level)

        with self.assertRaises(ValueError):
            FastLogger(self.fixture_logger, 'not a level')

    def test_is_active(self):
        fast_logger = FastLogger(self.fixture_logger, self.fixture_level.name)
        self.assertTrue(fast_logger.is_active())

    def test_get_level(self):
        for log_level in LogLevel:
            handler = StdOutHandler(name="handler_{}".format(log_level), level=log_level)
            logger = Logger("logger_{}".format(log_level), handler=handler)
            fast_logger = FastLogger(logger, 'info')
            self.assertEqual(fast_logger.get_level(), log_level)

    def test_fast_log(self):
        with CaptureOutput(relay=True) as capturer:
            fast_logger = FastLogger(self.fixture_logger, 'info')
            fast_logger.fast_log('msg')
            self.assertFalse(capturer.get_text())

        with CaptureOutput(relay=False) as capturer:
            fast_logger = FastLogger(self.fixture_logger, self.fixture_level.name)
            message = 'hi mom'
            fast_logger.fast_log(message)
            self.assertTrue(capturer.get_text().endswith(message))

    def test_config(self):
        debug_config = core.get_debug_logs_config(cfg_path=('tests', 'fixtures/config/debug.default.cfg'))
        debug_log_manager = DebugLogsManager().setup_logs(debug_config)

        file_logger = debug_log_manager.logs['de_sim.debug.testing.file']
        self.assertFalse(FastLogger(file_logger, 'debug').active)
        self.assertTrue(FastLogger(file_logger, 'info').active)

        console_logger = debug_log_manager.logs['de_sim.debug.testing.console']
        self.assertFalse(FastLogger(console_logger, 'debug').active)
        self.assertFalse(FastLogger(console_logger, 'info').active)
        self.assertTrue(FastLogger(console_logger, 'warning').active)

        debug_config = core.get_debug_logs_config()
        debug_log_manager = DebugLogsManager().setup_logs(debug_config)

        file_logger = debug_log_manager.logs['de_sim.debug.file']
        self.assertFalse(FastLogger(file_logger, 'debug').active)
