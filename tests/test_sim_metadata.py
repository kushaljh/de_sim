""" Test simulation metadata object

:Author: Jonathan Karr <karr@mssm.edu>
:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Date: 2017-08-18
:Copyright: 2016-2018, Karr Lab
:License: MIT
"""

import copy
import shutil
import tempfile
import unittest
from collections import namedtuple

from de_sim.sim_metadata import SimulationMetadata, AuthorMetadata, RunMetadata, Comparable
from wc_utils.util.git import get_repo_metadata, RepoMetadataCollectionType
from wc_utils.util.misc import as_dict
import wc_lang


SimulationConfig = namedtuple('SimulationConfig', 'time_max time_step changes perturbations random_seed')


class ExampleComparable(Comparable):

    ATTRIBUTES = ['attr', 'value']
    def __init__(self, attr, value):
        self.attr = attr
        self.value = value

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return False

        for attr in self.ATTRIBUTES:
            if getattr(other, attr) != getattr(self, attr):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class TestExampleComparable(unittest.TestCase):

    def test(self):
        ec1 = ExampleComparable('name', 1)
        ec2 = ExampleComparable('name_new', 2)
        obj = object()

        self.assertEqual(ec1, ec1)
        self.assertNotEqual(ec1, obj)
        self.assertNotEqual(ec1, ec2)


class TestSimulationMetadata(unittest.TestCase):

    def setUp(self):
        self.pickle_file_dir = tempfile.mkdtemp()

        model, _ = get_repo_metadata(repo_type=RepoMetadataCollectionType.SCHEMA_REPO)
        self.model = model

        changes = [
            ExampleComparable('name', 1),
            ExampleComparable('name_new', 2),
        ]

        perturbations = [
            ExampleComparable('perturbation_1', 3),
            ExampleComparable('perturbation_2', 4),
        ]

        simulation = SimulationConfig(100, 1, changes, perturbations, 1)

        self.author = author = AuthorMetadata(name='Test user', email='test@test.com',
                                              username='Test username', organization='Test organization')

        self.run = run = RunMetadata()
        run.record_start()
        run.record_ip_address()
        self.run_equal = copy.copy(run)
        self.run_different = copy.copy(run)
        self.run_different.record_end()

        self.metadata = SimulationMetadata(model, simulation, run, author)
        self.metadata_equal = SimulationMetadata(model, simulation, run, author)
        self.author_equal = copy.copy(author)
        self.author_different = author_different = copy.copy(author)
        author_different.name = 'Joe Smith'
        self.metadata_different = SimulationMetadata(model, simulation, run, author_different)

    def tearDown(self):
        shutil.rmtree(self.pickle_file_dir)

    def test_build_metadata(self):
        model = self.metadata.model
        self.assertIn(model.url, ['https://github.com/KarrLab/de_sim.git',
                                  'git@github.com:KarrLab/de_sim.git',
                                  'ssh://git@github.com/KarrLab/de_sim.git'])
        self.assertEqual(model.branch, 'master')

        run = self.metadata.run
        run.record_start()
        run.record_end()
        self.assertGreaterEqual(run.run_time, 0)

    def test_equality(self):
        obj = object()

        self.assertEqual(self.run, self.run_equal)
        self.assertNotEqual(self.run, obj)
        self.assertNotEqual(self.run, self.run_different)
        self.assertFalse(self.run != self.run_equal)

        self.assertEqual(self.author, self.author_equal)
        self.assertNotEqual(self.author, obj)
        self.assertNotEqual(self.author, self.author_different)

        self.assertEqual(self.metadata, self.metadata_equal)
        self.assertNotEqual(self.metadata, obj)
        self.assertNotEqual(self.metadata, self.metadata_different)

        self.assertEqual(self.metadata, self.metadata_equal)

    def test_as_dict(self):
        d = as_dict(self.metadata)
        self.assertEqual(d['author']['name'], self.metadata.author.name)
        self.assertEqual(d['model']['branch'], self.metadata.model.branch)
        self.assertEqual(d['run']['start_time'], self.metadata.run.start_time)
        self.assertEqual(d['simulation'].changes, self.metadata.simulation.changes)

    def test_str(self):
        self.assertIn(self.metadata.author.name, str(self.metadata))
        self.assertIn(self.metadata.model.branch, str(self.metadata))
        self.assertIn(self.metadata.run.ip_address, str(self.metadata))
        self.assertIn(str(self.metadata.simulation.time_max), str(self.metadata))

    def test_write_and_read(self):
        SimulationMetadata.write_metadata(self.metadata, self.pickle_file_dir)
        self.assertEqual(self.metadata, SimulationMetadata.read_metadata(self.pickle_file_dir))
