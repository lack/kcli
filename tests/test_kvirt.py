# coding=utf-8
import random
import string
import time
from kvirt.config import Kconfig
from kvirt.defaults import TEMPLATES


class TestK:
    @classmethod
    def setup_class(self):
        """

        """
        self.template = "cirros"
        self.config = Kconfig()
        self.k = self.config.k
        name = "test_%s" % ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        self.poolpath = "/var/lib/libvirt/%s" % name
        self.name = name

    def test_list(self):
        k = self.k
        result = k.list()
        assert result is not None

    def test_create_pool(self):
        k = self.k
        k.create_pool(name=self.name, poolpath=self.poolpath)
        print("prout")
        assert True

    def test_download_template(self):
        config = self.config
        result = config.handle_host(pool=self.name, templates=[self.template], download=True)
        assert result["result"] == "success"

    def test_create_network(self):
        k = self.k
        counter = random.randint(1, 254)
        k.create_network(name=self.name, cidr='10.0.%s.0/24' % counter, dhcp=True)
        assert True

    def test_create_vm(self):
        k = self.k
        time.sleep(10)
        k.create(self.name, numcpus=1, memory=512, pool=self.name, nets=[self.name])
        status = k.status(self.name)
        print(status)
        assert status is not None

    def test_add_disk(self):
        k = self.k
        k.add_disk(name=self.name, size=1, pool=self.name)
        assert True

    def test_stop_vm(self):
        k = self.k
        k.stop(self.name)
        status = k.status(self.name)
        assert status == 'down'

    def test_start_vm(self):
        k = self.k
        k.start(self.name)
        status = k.status(self.name)
        assert status == 'up'

    def test_delete_vm(self):
        k = self.k
        k.delete(self.name)
        status = k.status(self.name)
        assert status is None

    @classmethod
    def teardown_class(self):
        """

        """
        print("Cleaning stuff")
        k = self.k
        time.sleep(10)
        k.delete_network(self.name)
        k.delete_image(TEMPLATES[self.template])
        k.delete_pool(self.name, full=True)
