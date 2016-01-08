import unittest
import tempfile
import os
import shutil

import yaml

import neronet.config_parser as cp

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.fields = ['collection', 'run_command_prefix', 'main_code_file',
            'logoutput', 'parameters', 'parameters_format']
        self.values = ['test_collection', 'test_runner', 'main_code', 'output', 
                {'n': 1, 'x': 7}, '{n} {x}']
        self.testExperiment = {'test1': 
            {field: value for field, value in zip(self.fields, self.values)}}
        self.parser = cp.ConfigParser()
        self.testfolder = tempfile.mkdtemp()
        os.chdir(self.testfolder)
        self.expfolder = tempfile.mkdtemp(dir = self.testfolder)
        self.path = os.path.join(self.expfolder, cp.CONFIG_FILENAME)
        with open(self.path, 'w') as f:
            f.write("""
                    collection: test_collection
                    run_command_prefix: test_runner
                    main_code_file: main_code
                    logoutput: output
                    parameters: 
                        n: 1 
                        x: 7
                    parameters_format: '{n} {x}'
                    test1:
                    """)

    def tearDown(self):
        shutil.rmtree(self.testfolder)

    def testParseExperimentsSuccess(self):
        experiments = self.parser.parse_experiments(self.expfolder)
        for field, value in zip(self.fields, self.values):
            with self.subTest(value=value):
                self.assertEqual(experiments['test1'][field],
                self.testExperiment['test1'][field])

    def testRaisesFormatError(self):
        
    

def print_experiments(experiments):
    for experiment_id in sorted(experiments.keys()):
        print("Experiment", experiment_id)
        experiment = experiments[experiment_id]
        for field in sorted(experiment.keys()):
            print(field, experiment[field])

if __name__ == "__main__":
    unittest.main()
