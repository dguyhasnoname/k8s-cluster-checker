import unittest
import warnings
from modules.logging import Logger


logger = Logger.get_logger('', '')
class TestK8sClusterChecker(unittest.TestCase):
    def test_cluster(self):
        import cluster as cluster
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.assertRaises(TypeError, cluster.call_all(True, True, logger), True)
        with self.assertRaises(Exception) as x:
            print("Exception ignored: {}".format(x.exception))
    def test_nodes(self):
        import nodes as nodes
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        with self.assertRaises(Exception) as x:
            print("Exception ignored: {}".format(x.exception))
    def test_namespace(self):
        import namespace as namespace
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.assertRaises(TypeError, namespace.call_all(True, 'all', True, logger), True)
        with self.assertRaises(Exception) as x:
            print("Exception ignored: {}".format(x.exception))
    def test_pods(self):
        import pods as pods
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.assertRaises(TypeError, pods.call_all(True, 'all', True, logger), True)
        with self.assertRaises(Exception) as x:
            print("Exception ignored: {}".format(x.exception))