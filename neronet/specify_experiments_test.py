import unittest
import neroman

class TestSpecifyExperiments(unittest.TestCase):    
    def test_no_experiment_folder(self):
        testman = neroman.Neroman()
        with self.assertRaises(FileNotFoundError):
            testman.specify_experiment('/nonexistent')


    def test_no_config_file_in_folder(self):
        testman = neroman.Neroman()
        with self.assertRaises(FileNotFoundError):
            testman.specify_experiment('../test/experiments/emptyexp')


    def test_wrongly_formatted_config_file(self):
        pass


    def test_load_sleep(self):
        testman = neroman.Neroman()
        self.assertTrue(testman.specify_experiment('../test/experiments/sleep/'))
        
    def test_


if __name__ == '__main__':
    unittest.main()
