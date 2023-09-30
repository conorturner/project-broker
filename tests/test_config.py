import unittest
from app.modules import config


class ConfigTestCase(unittest.TestCase):
    def test_read_config(self):
        cfg = config.read_config('../configs/default.yaml')
        for k in ['port', 'secret', 'credentials', 'epics']:
            self.assertIn(k, cfg, msg=f'Config should contain a key for "{k}"')

        self.assertIn('capital', cfg['epics'])
        self.assertIn('ig', cfg['epics'])

        self.assertLessEqual(len(cfg['epics']['capital']), 40, msg='Should be less than 40 instruments in capital')
        self.assertLessEqual(len(cfg['epics']['ig']), 40, msg='Should be less than 40 instruments in ig')


if __name__ == '__main__':
    unittest.main()
