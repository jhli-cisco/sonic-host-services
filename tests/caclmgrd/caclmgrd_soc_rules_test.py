import os
import sys
import swsscommon

from parameterized import parameterized
from sonic_py_common.general import load_module_from_source
from ipaddress import IPv4Address, IPv4Network
from unittest import TestCase, mock
from pyfakefs.fake_filesystem_unittest import patchfs

from .test_soc_rules_vectors import CACLMGRD_SOC_TEST_VECTOR, CACLMGRD_SOC_TEST_VECTOR_EMPTY
from tests.common.mock_configdb import MockConfigDb
from unittest.mock import MagicMock, patch

DBCONFIG_PATH = '/var/run/redis/sonic-db/database_config.json'

class TestCaclmgrdSoc(TestCase):
    """
        Test caclmgrd soc
    """
    def setUp(self):
        swsscommon.swsscommon.ConfigDBConnector = MockConfigDb
        test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        modules_path = os.path.dirname(test_path)
        scripts_path = os.path.join(modules_path, "scripts")
        sys.path.insert(0, modules_path)
        caclmgrd_path = os.path.join(scripts_path, 'caclmgrd')
        self.caclmgrd = load_module_from_source('caclmgrd', caclmgrd_path)
        
    @parameterized.expand(CACLMGRD_SOC_TEST_VECTOR)
    @patchfs
    @patch('caclmgrd.get_ipv4_networks_from_interface_table', MagicMock(return_value=[IPv4Network('10.10.10.18/24', strict=False), IPv4Network('10.10.11.18/24', strict=False)]))
    def test_caclmgrd_soc(self, test_name, test_data, fs):
        if not os.path.exists(DBCONFIG_PATH):
            fs.create_file(DBCONFIG_PATH) # fake database_config.json

        MockConfigDb.set_config_db(test_data["config_db"])

        with mock.patch("caclmgrd.ControlPlaneAclManager.run_commands_pipe", return_value='sonic'):
            with mock.patch("caclmgrd.subprocess") as mocked_subprocess:
                popen_mock = mock.Mock()
                popen_attrs = test_data["popen_attributes"]
                popen_mock.configure_mock(**popen_attrs)
                mocked_subprocess.Popen.return_value = popen_mock
                mocked_subprocess.PIPE = -1

                call_rc = test_data["call_rc"]
                mocked_subprocess.call.return_value = call_rc

                caclmgrd_daemon = self.caclmgrd.ControlPlaneAclManager("caclmgrd")
                caclmgrd_daemon.update_control_plane_nat_acls('', {}, MockConfigDb())
                mocked_subprocess.Popen.assert_has_calls(test_data["expected_subprocess_calls"], any_order=True)


    @parameterized.expand(CACLMGRD_SOC_TEST_VECTOR_EMPTY)
    @patchfs
    @patch('caclmgrd.get_ipv4_networks_from_interface_table', MagicMock(return_value=[]))
    def test_caclmgrd_soc_no_ips(self, test_name, test_data, fs):
        if not os.path.exists(DBCONFIG_PATH):
            fs.create_file(DBCONFIG_PATH) # fake database_config.json

        MockConfigDb.set_config_db(test_data["config_db"])

        with mock.patch("caclmgrd.ControlPlaneAclManager.run_commands_pipe", return_value='sonic'):
            with mock.patch("caclmgrd.subprocess") as mocked_subprocess:
                popen_mock = mock.Mock()
                popen_attrs = test_data["popen_attributes"]
                popen_mock.configure_mock(**popen_attrs)
                mocked_subprocess.Popen.return_value = popen_mock
                mocked_subprocess.PIPE = -1

                call_rc = test_data["call_rc"]
                mocked_subprocess.call.return_value = call_rc

                caclmgrd_daemon = self.caclmgrd.ControlPlaneAclManager("caclmgrd")
                caclmgrd_daemon.update_control_plane_nat_acls('', {}, MockConfigDb())
                mocked_subprocess.Popen.assert_has_calls(test_data["expected_subprocess_calls"], any_order=True)


    @parameterized.expand(CACLMGRD_SOC_TEST_VECTOR_EMPTY)
    @patchfs
    @patch('caclmgrd.get_ipv4_networks_from_interface_table', MagicMock(return_value=['10.10.10.10']))
    def test_caclmgrd_soc_ip_string(self, test_name, test_data, fs):
        if not os.path.exists(DBCONFIG_PATH):
            fs.create_file(DBCONFIG_PATH) # fake database_config.json

        MockConfigDb.set_config_db(test_data["config_db"])

        with mock.patch("caclmgrd.ControlPlaneAclManager.run_commands_pipe", return_value='sonic'):
            with mock.patch("caclmgrd.subprocess") as mocked_subprocess:
                popen_mock = mock.Mock()
                popen_attrs = test_data["popen_attributes"]
                popen_mock.configure_mock(**popen_attrs)
                mocked_subprocess.Popen.return_value = popen_mock
                mocked_subprocess.PIPE = -1

                call_rc = test_data["call_rc"]
                mocked_subprocess.call.return_value = call_rc

                caclmgrd_daemon = self.caclmgrd.ControlPlaneAclManager("caclmgrd")
                caclmgrd_daemon.update_control_plane_nat_acls('', {}, MockConfigDb())
                mocked_subprocess.Popen.assert_has_calls(test_data["expected_subprocess_calls"], any_order=True)


    def test_get_ipv4_networks_from_interface_table(self):
        if not os.path.exists(DBCONFIG_PATH):
            fs.create_file(DBCONFIG_PATH) # fake database_config.json

        table = {("Vlan1000","10.10.10.1/32"): "val"}
        ip_addr = self.caclmgrd.get_ipv4_networks_from_interface_table(table, "Vlan")

        assert (ip_addr == [IPv4Network('10.10.10.1/32')])
