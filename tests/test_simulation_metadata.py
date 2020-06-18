""" Test discrete event simulation metadata object

:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2017-08-18
:Copyright: 2016-2018, Karr Lab
:License: MIT
"""

import copy
import dataclasses
import shutil
import tempfile
import unittest

from de_sim.errors import SimulatorError
from de_sim.simulation_config import SimulationConfig
from de_sim.simulation_metadata import SimulationMetadata, RunMetadata, AuthorMetadata
from wc_utils.util.git import get_repo_metadata, RepoMetadataCollectionType
from wc_utils.util.misc import obj_to_str


class TestSimulationMetadata(unittest.TestCase):

    def setUp(self):
        self.pickle_file_dir = tempfile.mkdtemp()

        simulator_repo, _ = get_repo_metadata(repo_type=RepoMetadataCollectionType.SCHEMA_REPO)
        self.simulator_repo = simulator_repo

        self.simulation_config = simulation_config = SimulationConfig(time_max=100, progress=False)

        self.author = author = AuthorMetadata(name='Test user', email='test@test.com',
                                              username='Test username', organization='Test organization')
        self.author_equal = copy.copy(author)
        self.author_different = author_different = copy.copy(author)
        author_different.name = 'Joe Smith'

        self.run = run = RunMetadata()
        run.record_start()
        run.record_ip_address()
        self.run_equal = copy.copy(run)
        self.run_different = copy.copy(run)
        self.run_different.record_run_time()

        self.metadata = SimulationMetadata(simulation_config, run, author, simulator_repo)
        self.metadata_equal = SimulationMetadata(simulation_config, run, author, simulator_repo)
        self.metadata_different = SimulationMetadata(simulation_config, run, author_different, simulator_repo)

    def tearDown(self):
        shutil.rmtree(self.pickle_file_dir)

    def test_build_metadata(self):
        run = self.metadata.run
        run.record_start()
        run.record_run_time()
        self.assertGreaterEqual(run.run_time, 0)

        simulator_repo = self.metadata.simulator_repo
        urls = ['https://github.com/KarrLab/de_sim.git',
                'git@github.com:KarrLab/de_sim.git',
                'ssh://git@github.com/KarrLab/de_sim.git']
        self.assertIn(simulator_repo.url.lower(), [url.lower() for url in urls])
        self.assertEqual(simulator_repo.branch, 'master')

    def test_author_metadata(self):
        author = AuthorMetadata(name='Arthur', email='test@test.com')
        self.assertIsInstance(author.username, str)

    def test_equality(self):
        obj = object()

        self.assertEqual(self.run, self.run_equal)
        self.assertNotEqual(self.run, obj)
        self.assertNotEqual(self.run, self.run_different)
        self.assertFalse(self.run != self.run_equal)

        self.assertEqual(self.author, self.author_equal)
        self.assertNotEqual(self.author, obj)
        self.assertNotEqual(self.author, self.author_different)

    def test_as_dict(self):
        d = dataclasses.asdict(self.metadata)
        self.assertEqual(d['simulation_config']['time_max'], self.metadata.simulation_config.time_max)
        self.assertEqual(d['author']['name'], self.metadata.author.name)
        self.assertEqual(d['run']['start_time'], self.metadata.run.start_time)
        self.assertEqual(d['simulator_repo']['branch'], self.metadata.simulator_repo.branch)

    def test_str(self):
        self.assertIn(str(self.simulation_config.time_max), str(self.metadata))
        self.assertIn(self.metadata.run.ip_address, str(self.metadata))
        self.assertIn(self.metadata.author.name, str(self.metadata))
        self.assertIn(self.metadata.simulator_repo.branch, str(self.metadata))

    def test_write_and_read(self):
        SimulationMetadata.write_dataclass(self.metadata, self.pickle_file_dir)
        self.assertEqual(self.metadata, SimulationMetadata.read_dataclass(self.pickle_file_dir))

    def test_exceptions(self):
        with self.assertRaisesRegexp(SimulatorError, 'name .* must be a str'):
            AuthorMetadata(name=11.0)
        with self.assertRaisesRegexp(SimulatorError, 'ip_address .* must be a str'):
            RunMetadata(ip_address=7)
        with self.assertRaisesRegexp(SimulatorError, 'simulation_config .* must be a SimulationConfig'):
            SimulationMetadata('hi', self.run, self.author)