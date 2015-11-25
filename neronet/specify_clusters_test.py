import unittest
import tempfile
import os
import neroman

class TestSpecifyClusters(unittest.TestCase):    
    
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.path = os.path.join(self.folder, 'clusters.yaml')
        with open(self.path, 'w') as f:
            f.write("clusters:\n"
                    "   triton:\n"
                    "       ssh_address: triton.aalto.fi\n"
                    "       type: slurm\n"
                    "\n"
                    "groups: null")
        self.testman = neroman.Neroman(clusters_file = self.path)
    
    def tearDown(self):
        os.remove(self.path)
        os.removedirs(self.folder)


    def test_load_clusters_from_clusters_yaml(self):
        self.assertEqual(self.testman.clusters['clusters']['triton']\
                        ['ssh_address'], 'triton.aalto.fi')
        self.assertEqual(self.testman.clusters['clusters']['triton']\
                        ['type'], 'slurm')

    def test_specify_clusters_normal(self):
        self.testman.specify_cluster('testcluster', 
                'testcluster.com', 'unmanaged')
        self.assertEqual(self.testman.clusters['clusters']['testcluster']\
                        ['type'], 'unmanaged')
        self.assertEqual(self.testman.clusters['clusters']['testcluster']\
                        ['ssh_address'], 'testcluster.com')

    def test_specify_clusters_bad_cluster_type(self):
        self.assertRaises(neroman.FormatError, 
                self.testman.specify_cluster, 'testcluster', 'testcluster.com', 'badclustertype')


if __name__ == '__main__':
    unittest.main()
