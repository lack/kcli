#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kvirt config class
"""

from distutils.spawn import find_executable
from kvirt.defaults import (NETS, POOL, CPUMODEL, NUMCPUS, MEMORY, DISKS,
                            DISKSIZE, DISKINTERFACE, DISKTHIN, GUESTID,
                            VNC, CLOUDINIT, RESERVEIP, RESERVEDNS, RESERVEHOST,
                            START, AUTOSTART, NESTED, TUNNEL, REPORTURL, REPORTDIR,
                            REPORT, REPORTALL, INSECURE, KEYS, CMDS, DNS,
                            DOMAIN, SCRIPTS, FILES, ISO,
                            NETMASKS, GATEWAY, SHAREDKEY, IMAGE, ENABLEROOT,
                            PLANVIEW, PRIVATEKEY, TAGS, RHNREGISTER, RHNUSER, RHNPASSWORD, RHNAK, RHNORG, RHNPOOL,
                            FLAVOR, KEEP_NETWORKS, DNSCLIENT, STORE_METADATA, NOTIFY, NOTIFYTOKEN, NOTIFYCMD,
                            SHAREDFOLDERS, KERNEL, INITRD, CMDLINE, PLACEMENT, YAMLINVENTORY, CPUHOTPLUG, MEMORYHOTPLUG)
from kvirt import common
import os
from shutil import copytree, rmtree
import yaml
from jinja2 import Environment, FileSystemLoader
from jinja2 import StrictUndefined as strictundefined
from jinja2.runtime import Undefined as defaultundefined
from jinja2.exceptions import TemplateSyntaxError, TemplateError
import re


class Kbaseconfig:
    """

    """
    def __init__(self, client=None, containerclient=None, debug=False, quiet=False):
        homedir = os.environ.get('HOME')
        cmdir = "%s/.kcli_cm" % homedir
        kclidir = "%s/.kcli" % homedir
        if os.path.isdir(cmdir) and not os.path.isdir(kclidir):
            copytree(cmdir, kclidir)
        inifile = "%s/.kcli/config.yml" % homedir
        secretsfile = "%s/.kcli/secrets.yml" % homedir
        if not os.path.exists(secretsfile):
            secrets = {}
        else:
            with open(secretsfile, 'r') as entries:
                try:
                    secrets = yaml.safe_load(entries)
                except yaml.scanner.ScannerError as err:
                    common.pprint("Couldn't parse yaml in .kcli/secrets.yml. Got %s" % err, color='red')
                    os._exit(1)
        if not os.path.exists(inifile):
            defaultclient = 'local'
            if os.path.exists('/var/run/libvirt/libvirt-sock'):
                _type = 'kvm'
            else:
                common.pprint("No configuration found nor local hypervisor", color='red')
                os._exit(1)
            self.ini = {'default': {'client': defaultclient}, defaultclient:
                        {'pool': 'default', 'type': _type}}
        else:
            with open(inifile, 'r') as entries:
                try:
                    self.ini = yaml.safe_load(entries)
                except yaml.scanner.ScannerError as err:
                    common.pprint("Couldn't parse yaml in .kcli/config.yml. Got %s" % err, color='red')
                    os._exit(1)
                except:
                    self.host = None
                    return
            for key1 in self.ini:
                for key2 in self.ini[key1]:
                    if isinstance(self.ini[key1][key2], str) and self.ini[key1][key2] == '?secret':
                        if key1 in secrets and key2 in secrets[key1]:
                            self.ini[key1][key2] = secrets[key1][key2]
                        else:
                            common.pprint("Missing secret for %s/%s" % (key1, key2), color='red')
                            os._exit(1)
            if 'default' not in self.ini:
                if len(self.ini) == 1:
                    client = list(self.ini.keys())[0]
                    self.ini['default'] = {"client": client}
                else:
                    common.pprint("Missing default section in config file. Leaving...", color='red')
                    self.host = None
                    return
            if 'client' not in self.ini['default']:
                if not quiet:
                    common.pprint("Using local libvirt as no client was specified...")
                self.ini['default']['client'] = 'local'
                self.ini['local'] = {}
        self.clients = [e for e in self.ini if e != 'default']
        defaults = {}
        default = self.ini['default']
        defaults['nets'] = default.get('nets', NETS)
        defaults['pool'] = default.get('pool', POOL)
        defaults['image'] = default.get('image', IMAGE)
        defaults['cpumodel'] = default.get('cpumodel', CPUMODEL)
        defaults['numcpus'] = int(default.get('numcpus', NUMCPUS))
        defaults['memory'] = int(default.get('memory', MEMORY))
        defaults['disks'] = default.get('disks', DISKS)
        defaults['disksize'] = default.get('disksize', DISKSIZE)
        defaults['diskinterface'] = default.get('diskinterface', DISKINTERFACE)
        defaults['diskthin'] = default.get('diskthin', DISKTHIN)
        defaults['guestid'] = default.get('guestid', GUESTID)
        defaults['vnc'] = bool(default.get('vnc', VNC))
        defaults['cloudinit'] = bool(default.get('cloudinit', CLOUDINIT))
        defaults['reserveip'] = bool(default.get('reserveip', RESERVEIP))
        defaults['reservedns'] = bool(default.get('reservedns', RESERVEDNS))
        defaults['reservehost'] = bool(default.get('reservehost', RESERVEHOST))
        defaults['nested'] = bool(default.get('nested', NESTED))
        defaults['start'] = bool(default.get('start', START))
        defaults['autostart'] = bool(default.get('autostart', AUTOSTART))
        defaults['tunnel'] = bool(default.get('tunnel', TUNNEL))
        defaults['insecure'] = bool(default.get('insecure', INSECURE))
        defaults['reporturl'] = default.get('reporturl', REPORTURL)
        defaults['reportdir'] = default.get('reportdir', REPORTDIR)
        defaults['report'] = bool(default.get('report', REPORT))
        defaults['reportall'] = bool(default.get('reportall', REPORTALL))
        defaults['keys'] = default.get('keys', KEYS)
        defaults['cmds'] = default.get('cmds', CMDS)
        defaults['dns'] = default.get('dns', DNS)
        defaults['domain'] = default.get('file', DOMAIN)
        defaults['scripts'] = default.get('script', SCRIPTS)
        defaults['files'] = default.get('files', FILES)
        defaults['iso'] = default.get('iso', ISO)
        defaults['netmasks'] = default.get('netmasks', NETMASKS)
        defaults['gateway'] = default.get('gateway', GATEWAY)
        defaults['sharedkey'] = default.get('sharedkey', SHAREDKEY)
        defaults['enableroot'] = default.get('enableroot', ENABLEROOT)
        defaults['planview'] = default.get('planview', PLANVIEW)
        defaults['privatekey'] = default.get('privatekey', PRIVATEKEY)
        defaults['rhnregister'] = default.get('rhnregister', RHNREGISTER)
        defaults['rhnuser'] = default.get('rhnuser', RHNUSER)
        defaults['rhnpassword'] = default.get('rhnpassword', RHNPASSWORD)
        defaults['rhnactivationkey'] = default.get('rhnactivationkey', RHNAK)
        defaults['rhnorg'] = default.get('rhnorg', RHNORG)
        defaults['rhnpool'] = default.get('rhnpool', RHNPOOL)
        defaults['tags'] = default.get('tags', TAGS)
        defaults['flavor'] = default.get('flavor', FLAVOR)
        defaults['keep_networks'] = default.get('keep_networks', KEEP_NETWORKS)
        defaults['dnsclient'] = default.get('dnsclient', DNSCLIENT)
        defaults['storemetadata'] = default.get('storemetadata', STORE_METADATA)
        defaults['notify'] = default.get('notify', NOTIFY)
        defaults['notifytoken'] = default.get('notifytoken', NOTIFYTOKEN)
        defaults['notifycmd'] = default.get('notifycmd', NOTIFYCMD)
        defaults['sharedfolders'] = default.get('sharedfolders', SHAREDFOLDERS)
        defaults['kernel'] = default.get('kernel', KERNEL)
        defaults['initrd'] = default.get('initrd', INITRD)
        defaults['cmdline'] = default.get('cmdline', CMDLINE)
        defaults['placement'] = default.get('placement', PLACEMENT)
        defaults['yamlinventory'] = default.get('yamlinventory', YAMLINVENTORY)
        defaults['cpuhotplug'] = bool(default.get('cpuhotplug', CPUHOTPLUG))
        defaults['memoryhotplug'] = bool(default.get('memoryhotplug', MEMORYHOTPLUG))
        currentplanfile = "%s/.kcli/plan" % os.environ.get('HOME')
        if os.path.exists(currentplanfile):
            self.currentplan = open(currentplanfile).read().strip()
        else:
            self.currentplan = 'kvirt'
        self.default = defaults
        profilefile = default.get('profiles', "%s/.kcli/profiles.yml" %
                                  os.environ.get('HOME'))
        profilefile = os.path.expanduser(profilefile)
        if not os.path.exists(profilefile):
            self.profiles = {}
        else:
            with open(profilefile, 'r') as entries:
                self.profiles = yaml.safe_load(entries)
                if self.profiles is None:
                    self.profiles = {}
        flavorsfile = default.get('flavors', "%s/.kcli/flavors.yml" %
                                  os.environ.get('HOME'))
        flavorsfile = os.path.expanduser(flavorsfile)
        if not os.path.exists(flavorsfile):
            self.flavors = {}
        else:
            with open(flavorsfile, 'r') as entries:
                try:
                    self.flavors = yaml.safe_load(entries)
                except yaml.scanner.ScannerError as err:
                    common.pprint("Couldn't parse yaml in .kcli/flavors.yml. Leaving...", color='red')
                    common.pprint(err, color='red')
                    os._exit(1)
        self.extraclients = {}
        self._extraclients = []
        if client == 'all':
            clis = [cli for cli in self.clients if
                    self.ini[cli].get('enabled', True)]
            self.client = clis[0]
            self._extraclients = clis[1:]
        elif client is None:
            self.client = self.ini['default']['client']
        elif ',' in client:
            self.client = client.split(',')[0]
            self._extraclients = client.split(',')[1:]
        else:
            self.client = client
        if self.client not in self.ini:
            common.pprint("Missing section for client %s in config file. Trying to connect..." % self.client,
                          color='blue')
            self.ini[self.client] = {'host': self.client}
        self.options = self.ini[self.client]
        options = self.options
        self.enabled = options.get('enabled', True)
        if not self.enabled:
            common.pprint("Disabled hypervisor %s.Leaving..." % client, color='red')
            os._exit(1)
        self.host = options.get('host', '127.0.0.1')
        self.port = options.get('port', 22)
        self.user = options.get('user', 'root')
        self.protocol = options.get('protocol', 'ssh')
        self.type = options.get('type', 'kvm')
        self.url = options.get('url', None)
        self.pool = options.get('pool', self.default['pool'])
        self.image = options.get('image', self.default['image'])
        self.tunnel = bool(options.get('tunnel', self.default['tunnel']))
        self.insecure = bool(options.get('insecure', self.default['insecure']))
        self.report = options.get('report', self.default['report'])
        self.reporturl = options.get('reporturl', self.default['reportdir'])
        self.reportdir = options.get('reportdir', self.default['reportdir'])
        self.reportall = options.get('reportall', self.default['reportall'])
        self.nets = options.get('nets', self.default['nets'])
        self.cpumodel = options.get('cpumodel', self.default['cpumodel'])
        self.cpuflags = options.get('cpuflags', [])
        self.numcpus = options.get('numcpus', self.default['numcpus'])
        self.memory = options.get('memory', self.default['memory'])
        self.disks = options.get('disks', self.default['disks'])
        self.disksize = options.get('disksize', self.default['disksize'])
        self.diskinterface = options.get('diskinterface',
                                         self.default['diskinterface'])
        self.diskthin = options.get('diskthin', self.default['diskthin'])
        self.guestid = options.get('guestid', self.default['guestid'])
        self.vnc = options.get('vnc', self.default['vnc'])
        self.cloudinit = options.get('cloudinit', self.default['cloudinit'])
        self.reserveip = options.get('reserveip', self.default['reserveip'])
        self.reservedns = options.get('reservedns', self.default['reservedns'])
        self.reservehost = options.get('reservehost',
                                       self.default['reservehost'])
        self.nested = options.get('nested', self.default['nested'])
        self.start = options.get('start', self.default['start'])
        self.autostart = options.get('autostart', self.default['autostart'])
        self.iso = options.get('iso', self.default['iso'])
        self.keys = options.get('keys', self.default['keys'])
        self.cmds = options.get('cmds', self.default['cmds'])
        self.netmasks = options.get('netmasks', self.default['netmasks'])
        self.gateway = options.get('gateway', self.default['gateway'])
        self.sharedkey = options.get('sharedkey', self.default['sharedkey'])
        self.enableroot = options.get('enableroot', self.default['enableroot'])
        self.planview = options.get('planview', self.default['planview'])
        self.dns = options.get('dns', self.default['dns'])
        self.domain = options.get('domain', self.default['domain'])
        self.scripts = options.get('scripts', self.default['scripts'])
        self.files = options.get('files', self.default['files'])
        self.privatekey = options.get('privatekey', self.default['privatekey'])
        self.rhnregister = options.get('rhnregister', self.default['rhnregister'])
        self.rhnuser = options.get('rhnuser', self.default['rhnuser'])
        self.rhnpassword = options.get('rhnpassword', self.default['rhnpassword'])
        self.rhnak = options.get('rhnactivationkey', self.default['rhnactivationkey'])
        self.rhnorg = options.get('rhnorg', self.default['rhnorg'])
        self.rhnpool = options.get('rhnpool', self.default['rhnpool'])
        self.tags = options.get('tags', self.default['tags'])
        self.flavor = options.get('flavor', self.default['flavor'])
        self.dnsclient = options.get('dnsclient', self.default['dnsclient'])
        self.storemetadata = options.get('storemetadata', self.default['storemetadata'])
        self.notify = options.get('notify', self.default['notify'])
        self.notifytoken = options.get('notifytoken', self.default['notifytoken'])
        self.notifycmd = options.get('notifycmd', self.default['notifycmd'])
        self.keep_networks = options.get('keep_networks', self.default['keep_networks'])
        self.sharedfolders = options.get('sharedfolders', self.default['sharedfolders'])
        self.kernel = options.get('kernel', self.default['kernel'])
        self.initrd = options.get('initrd', self.default['initrd'])
        self.cmdline = options.get('cmdline', self.default['cmdline'])
        self.placement = options.get('placement', self.default['placement'])
        self.yamlinventory = options.get('yamlinventory', self.default['yamlinventory'])
        self.cpuhotplug = options.get('cpuhotplug', self.default['cpuhotplug'])
        self.memoryhotplug = options.get('memoryhotplug', self.default['memoryhotplug'])
        self.containerclient = containerclient
        self.overrides = {}

    def switch_host(self, client):
        """

        :param client:
        :return:
        """
        if client not in self.clients:
            common.pprint("Client %s not found in config.Leaving...." % client,
                          color='red')
            return {'result': 'failure', 'reason': "Client %s not found in config" % client}
        enabled = self.ini[client].get('enabled', True)
        if not enabled:
            common.pprint("Client %s is disabled.Leaving...." % client,
                          color='red')
            return {'result': 'failure', 'reason': "Client %s is disabled" %
                    client}
        common.pprint("Switching to client %s..." % client)
        self.ini['default']['client'] = client
        inifile = "%s/.kcli/config.yml" % os.environ.get('HOME')
        with open(inifile, 'w') as conf_file:
            yaml.safe_dump(self.ini, conf_file, default_flow_style=False, encoding='utf-8', allow_unicode=True,
                           sort_keys=False)
        return {'result': 'success'}

    def enable_host(self, client):
        """

        :param client:
        :return:
        """
        if client not in self.clients:
            common.pprint("Client %s not found in config.Leaving...." % client)
            return {'result': 'failure', 'reason': "Client %s not found in config" % client}
        common.pprint("Enabling client %s..." % client)
        self.ini[client]['enabled'] = True
        inifile = "%s/.kcli/config.yml" % os.environ.get('HOME')
        with open(inifile, 'w') as conf_file:
            yaml.safe_dump(self.ini, conf_file, default_flow_style=False, encoding='utf-8', allow_unicode=True,
                           sort_keys=False)
        return {'result': 'success'}

    def disable_host(self, client):
        """

        :param client:
        :return:
        """
        if client not in self.clients:
            common.pprint("Client %s not found in config.Leaving...." % client,
                          color='red')
            return {'result': 'failure', 'reason': "Client %s not found in config" % client}
        elif self.ini['default']['client'] == client:
            common.pprint("Client %s currently default.Leaving...." % client,
                          color='red')
            return {'result': 'failure', 'reason': "Client %s currently default" % client}
        common.pprint("Disabling client %s..." % client)
        self.ini[client]['enabled'] = False
        inifile = "%s/.kcli/config.yml" % os.environ.get('HOME')
        with open(inifile, 'w') as conf_file:
            yaml.safe_dump(self.ini, conf_file, default_flow_style=False, encoding='utf-8', allow_unicode=True,
                           sort_keys=False)
        return {'result': 'success'}

    def set_defaults(self):
        """

        """
        default = {}
        for key in sorted(self.default):
            if self.default[key] is None or (isinstance(self.default[key], list) and not self.default[key]):
                continue
            else:
                default[key] = self.default[key]
        sort_keys = False
        if len(self.clients) == 1:
            default['client'] = [*self.clients][0]
            sort_keys = True
        self.ini['default'] = default
        path = os.path.expanduser('~/.kcli/config.yml')
        with open(path, 'w') as conf_file:
            yaml.safe_dump(self.ini, conf_file, default_flow_style=False, encoding='utf-8', allow_unicode=True,
                           sort_keys=sort_keys)

    def list_keywords(self):
        """

        """
        return self.default

    def list_repos(self):
        """

        :return:
        """
        repos = {}
        plansdir = "%s/.kcli/plans" % os.environ.get('HOME')
        if not os.path.exists(plansdir):
            return {}
        else:
            repodirs = [d for d in os.listdir(plansdir) if os.path.isdir("%s/%s" % (plansdir, d))]
            for d in repodirs:
                repos[d] = None
                if os.path.exists("%s/%s/.git/config" % (plansdir, d)) and find_executable('git') is not None:
                    gitcmd = "git config -f %s/%s/.git/config  --get remote.origin.url" % (plansdir, d)
                    giturl = os.popen(gitcmd).read().strip()
                    repos[d] = giturl
        return repos

    def list_products(self, group=None, repo=None):
        """

        :param group:
        :param repo:
        :return:
        """
        plansdir = "%s/.kcli/plans" % os.environ.get('HOME')
        if not os.path.exists(plansdir):
            return []
        else:
            products = []
            repodirs = [d for d in os.listdir(plansdir) if os.path.isdir("%s/%s" % (plansdir, d))]
            for rep in repodirs:
                repometa = "%s/%s/KMETA" % (plansdir, rep)
                if not os.path.exists(repometa):
                    continue
                else:
                    realdir = os.path.dirname(os.readlink(repometa)) if os.path.islink(repometa) else None
                    with open(repometa, 'r') as entries:
                        try:
                            repoproducts = yaml.safe_load(entries)
                            for repoproduct in repoproducts:
                                repoproduct['repo'] = rep
                                if 'file' not in repoproduct:
                                    repoproduct['file'] = 'kcli_plan.yml'
                                if '/' in repoproduct['file']:
                                    repoproduct['group'] = repoproduct['file'].split('/')[0]
                                else:
                                    repoproduct['group'] = ''
                                if realdir is not None:
                                    repoproduct['realdir'] = realdir
                                products.append(repoproduct)
                        except yaml.scanner.ScannerError:
                            common.pprint("Couldn't properly parse .kcli/repo. Leaving...", color='red')
                            continue
            if repo is not None:
                products = [product for product in products if 'repo'
                            in product and product['repo'] == repo]
            if group is not None:
                products = [product for product in products if 'group'
                            in product and product['group'] == group]
            return products

    def create_repo(self, name, url):
        """

        :param name:
        :param url:
        :return:
        """
        reponame = name if name is not None else os.path.basename(url)
        repodir = "%s/.kcli/plans/%s" % (os.environ.get('HOME'), reponame)
        if not os.path.exists(repodir):
            os.makedirs(repodir, exist_ok=True)
        if not url.startswith('http') and not url.startswith('git'):
            os.symlink(url, repodir)
        elif find_executable('git') is None:
            common.pprint('repo operations require git', color='red')
            os._exit(1)
        else:
            os.system("git clone %s %s" % (url, repodir))
        if not os.path.exists("%s/KMETA" % repodir):
            for root, dirs, files in os.walk(repodir):
                for name in files:
                    if name == 'KMETA':
                        dst = "%s/KMETA" % repodir
                        src = "%s/KMETA" % root.replace("%s/" % repodir, '')
                        os.symlink(src, dst)
                        break
        os._exit(1)

    def update_repo(self, name, url=None):
        """

        :param name:
        :param url:
        :return:
        """
        repodir = "%s/.kcli/plans/%s" % (os.environ.get('HOME'), name)
        if not os.path.exists(repodir):
            return {'result': 'failure', 'reason': 'repo %s not found' % name}
        elif find_executable('git') is None:
            return {'result': 'failure', 'reason': 'repo operations require git'}
        else:
            os.chdir(repodir)
            if os.path.exists('.git'):
                os.system("git pull --rebase")
        return {'result': 'success'}

    def delete_repo(self, name):
        """

        :param name:
        :return:
        """
        repodir = "%s/.kcli/plans/%s" % (os.environ.get('HOME'), name)
        if os.path.exists(repodir) and os.path.isdir(repodir):
            rmtree(repodir)
            return {'result': 'success'}

    def info_plan(self, inputfile, quiet=False, web=False, onfly=None):
        """

        :param inputfile:
        :param quiet:
        :return:
        """
        inputfile = os.path.expanduser(inputfile) if inputfile is not None else 'kcli_plan.yml'
        if not quiet:
            common.pprint("Providing information on parameters of plan %s..." % inputfile)
        if not os.path.exists(inputfile):
            common.pprint("No input file found nor default kcli_plan.yml. Leaving....", color='red')
            os._exit(1)
        parameters = common.get_parameters(inputfile)
        if parameters is not None:
            parameters = yaml.safe_load(parameters)['parameters']
            if web:
                return parameters
            for parameter in parameters:
                print("%s: %s" % (parameter, parameters[parameter]))
                if parameter == 'baseplan':
                    if onfly is not None:
                        common.fetch("%s/%s" % (onfly, parameters[parameter]), '.')
                    baseplan = parameters[parameter]
                    basedir = os.path.dirname(inputfile) if os.path.basename(inputfile) != inputfile else '.'
                    baseplan = "%s/%s" % (basedir, baseplan)
                    self.info_plan(baseplan, quiet=True)
                    print()
        else:
            common.pprint("No parameters found. Leaving...", color='blue')
        # return {'result': 'success'}

    def info_product(self, name, repo=None, group=None, web=False):
        """Info product"""
        if repo is not None and group is not None:
            products = [product for product in self.list_products
                        if product['name'] == name and product['repo'] == repo and product['group'] == group]
        elif repo is not None:
            products = [product for product in self.list_products()
                        if product['name'] == name and product['repo'] == repo]
        if group is not None:
            products = [product for product in self.list_products()
                        if product['name'] == name and product['group'] == group]
        else:
            products = [product for product in self.list_products() if product['name'] == name]
        if len(products) == 0:
            common.pprint("Product not found. Leaving...", color='red')
            os._exit(1)
        elif len(products) > 1:
            common.pprint("Product found in several places. Specify repo or group", color='red')
            os._exit(1)
        else:
            product = products[0]
            repo = product['repo']
            repodir = "%s/.kcli/plans/%s" % (os.environ.get('HOME'), repo)
            group = product['group']
            _file = product['file']
            description = product.get('description')
            numvms = product.get('numvms')
            image = product.get('image')
            comments = product.get('comments')
            if not web:
                if description is not None:
                    print("description: %s" % description)
                if group is not None:
                    print("group: %s" % group)
                if numvms is not None:
                    numvmsinfo = "numvms: %s" % numvms
                    if numvms == 1:
                        numvmsinfo += " (Vm name can be overriden)"
                    print(numvmsinfo)
                if image is not None:
                    print("image: %s" % image)
                if comments is not None:
                    print("Comments : %s" % comments)
            inputfile = "%s/%s" % (product['realdir'], _file) if 'realdir' in product else _file
            parameters = self.info_plan("%s/%s" % (repodir, inputfile), quiet=True, web=web)
            if web:
                return {'product': product, 'comments': comments, 'description': description, 'parameters': parameters}

    def process_inputfile(self, plan, inputfile, overrides={}, onfly=None, full=False, ignore=False,
                          download_mode=False):
        basedir = os.path.dirname(inputfile) if os.path.dirname(inputfile) != '' else '.'
        basefile = None
        undefined = strictundefined if not ignore else defaultundefined
        env = Environment(loader=FileSystemLoader(basedir), undefined=undefined)
        try:
            templ = env.get_template(os.path.basename(inputfile))
        except TemplateSyntaxError as e:
            common.pprint("Error rendering line %s of file %s. Got: %s" % (e.lineno, e.filename, e.message),
                          color='red')
            os._exit(1)
        except TemplateError as e:
            common.pprint("Error rendering file %s. Got: %s" % (inputfile, e.message), color='red')
            os._exit(1)
        parameters = common.get_parameters(inputfile)
        if parameters is not None:
            parameters = yaml.safe_load(parameters)['parameters']
            if not isinstance(parameters, dict):
                common.pprint("Error rendering parameters section of file %s" % inputfile, color='red')
                os._exit(1)
            for parameter in parameters:
                if parameter == 'baseplan':
                    basefile = parameters['baseplan']
                    if onfly is not None:
                        common.fetch("%s/%s" % (onfly, basefile), '.')
                    baseparameters = common.get_parameters(basefile)
                    if baseparameters is not None:
                        baseparameters = yaml.safe_load(baseparameters)['parameters']
                        for baseparameter in baseparameters:
                            if baseparameter not in overrides and baseparameter not in parameters:
                                overrides[baseparameter] = baseparameters[baseparameter]
                elif parameter not in overrides:
                    currentparameter = parameters[parameter]
                    if isinstance(currentparameter, bool) and download_mode:
                        currentparameter = True
                    overrides[parameter] = currentparameter
        with open(inputfile, 'r') as entries:
            overrides.update(self.overrides)
            overrides.update({'plan': plan})
            try:
                entries = templ.render(overrides)
            except TemplateError as e:
                common.pprint("Error rendering inputfile %s. Got: %s" % (inputfile, e.message), color='red')
                os._exit(1)
            if not full:
                entrieslist = entries.split('\n')
                if entrieslist[0].startswith('parameters:'):
                    for index, line in enumerate(entrieslist[1:]):
                        if re.match(r'\S', line):
                            entries = '\n'.join(entrieslist[index + 1:])
                            break
                return entries
            entries = yaml.safe_load(entries)
        return entries, overrides, basefile, basedir

    def list_profiles(self):
        """

        :return:
        """
        default_disksize = '10'
        default = self.default
        results = []
        for profile in [p for p in self.profiles if 'base' not in self.profiles[p]] + [p for p in self.profiles
                                                                                       if 'base' in self.profiles[p]]:
            info = self.profiles[profile]
            if 'base' in info:
                father = self.profiles[info['base']]
                default_numcpus = father.get('numcpus', default['numcpus'])
                default_memory = father.get('memory', default['memory'])
                default_pool = father.get('pool', default['pool'])
                default_disks = father.get('disks', default['disks'])
                default_nets = father.get('nets', default['nets'])
                default_image = father.get('image', '')
                default_cloudinit = father.get('cloudinit', default['cloudinit'])
                default_nested = father.get('nested', default['nested'])
                default_reservedns = father.get('reservedns', default['reservedns'])
                default_reservehost = father.get('reservehost', default['reservehost'])
                default_flavor = father.get('flavor', default['flavor'])
            else:
                default_numcpus = default['numcpus']
                default_memory = default['memory']
                default_pool = default['pool']
                default_disks = default['disks']
                default_nets = default['nets']
                default_image = ''
                default_cloudinit = default['cloudinit']
                default_nested = default['nested']
                default_reservedns = default['reservedns']
                default_reservehost = default['reservehost']
                default_flavor = default['flavor']
            profiletype = info.get('type', '')
            if profiletype == 'container':
                continue
            numcpus = info.get('numcpus', default_numcpus)
            memory = info.get('memory', default_memory)
            pool = info.get('pool', default_pool)
            diskinfo = []
            disks = info.get('disks', default_disks)
            for disk in disks:
                if disk is None:
                    size = default_disksize
                elif isinstance(disk, int):
                    size = str(disk)
                elif isinstance(disk, dict):
                    size = str(disk.get('size', default_disksize))
                diskinfo.append(size)
            diskinfo = ','.join(diskinfo)
            netinfo = []
            nets = info.get('nets', default_nets)
            for net in nets:
                if isinstance(net, str):
                    netname = net
                elif isinstance(net, dict) and 'name' in net:
                    netname = net['name']
                netinfo.append(netname)
            netinfo = ','.join(netinfo)
            template = info.get('template', default_image)
            image = info.get('image', template)
            cloudinit = info.get('cloudinit', default_cloudinit)
            nested = info.get('nested', default_nested)
            reservedns = info.get('reservedns', default_reservedns)
            reservehost = info.get('reservehost', default_reservehost)
            flavor = info.get('flavor', default_flavor)
            if flavor is None:
                flavor = "%scpus %sMb ram" % (numcpus, memory)
            results.append([profile, flavor, pool, diskinfo, image, netinfo, cloudinit, nested,
                            reservedns, reservehost])
        return sorted(results, key=lambda x: x[0])

    def list_flavors(self):
        """

        :return:
        """
        results = []
        for flavor in self.flavors:
            info = self.flavors[flavor]
            numcpus = info.get('numcpus')
            memory = info.get('memory')
            disk = info.get('disk', '')
            if numcpus is not None and memory is not None:
                results.append([flavor, numcpus, memory, disk])
        return sorted(results, key=lambda x: x[0])

    def list_containerprofiles(self):
        """

        :return:
        """
        results = []
        for profile in sorted(self.profiles):
            info = self.profiles[profile]
            if 'type' not in info or info['type'] != 'container':
                continue
            else:
                image = next((e for e in [info.get('image'), info.get('image')] if e is not None), '')
                nets = info.get('nets', '')
                ports = info.get('ports', '')
                volumes = next((e for e in [info.get('volumes'), info.get('disks')] if e is not None), '')
                # environment = profile.get('environment', '')
                cmd = info.get('cmd', '')
                results.append([profile, image, nets, ports, volumes, cmd])
        return results

    def delete_profile(self, profile, quiet=False):
        if profile not in self.profiles:
            if quiet:
                common.pprint("Profile %s not found" % profile, color='red')
            return {'result': 'failure', 'reason': 'Profile %s not found' % profile}
        else:
            del self.profiles[profile]
            path = os.path.expanduser('~/.kcli/profiles.yml')
            if not self.profiles:
                os.remove(path)
            else:
                with open(path, 'w') as profile_file:
                    yaml.safe_dump(self.profiles, profile_file, default_flow_style=False, encoding='utf-8',
                                   allow_unicode=True, sort_keys=False)
            return {'result': 'success'}

    def create_profile(self, profile, overrides={}, quiet=False):
        if profile in self.profiles:
            if not quiet:
                common.pprint("Profile %s already there" % profile, color='blue')
            return {'result': 'success'}
        if not overrides:
            return {'result': 'failure', 'reason': "You need to specify at least one parameter"}
        path = os.path.expanduser('~/.kcli/profiles.yml')
        rootdir = os.path.expanduser('~/.kcli')
        self.profiles[profile] = overrides
        if not os.path.exists(rootdir):
            os.makedirs(rootdir)
        with open(path, 'w') as profile_file:
            yaml.safe_dump(self.profiles, profile_file, default_flow_style=False, encoding='utf-8',
                           allow_unicode=True, sort_keys=False)
        return {'result': 'success'}

    def update_profile(self, profile, overrides={}, quiet=False):
        if profile not in self.profiles:
            if quiet:
                common.pprint("Profile %s not found" % profile, color='red')
            return {'result': 'failure', 'reason': 'Profile %s not found' % profile}
        if not overrides:
            return {'result': 'failure', 'reason': "You need to specify at least one parameter"}
        path = os.path.expanduser('~/.kcli/profiles.yml')
        self.profiles[profile].update(overrides)
        with open(path, 'w') as profile_file:
            yaml.safe_dump(self.profiles, profile_file, default_flow_style=False, encoding='utf-8',
                           allow_unicode=True, sort_keys=False)
        return {'result': 'success'}
