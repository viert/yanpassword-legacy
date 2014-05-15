from setuptools import setup, find_packages

setup(
    name = "YanPassword",
    version = "0.9-rc1",
    packages = find_packages(),

    scripts = [ 'yanpassword.py' ],
    install_requires = [ 'pycrypto' ],

    author = "Pavel Vorobyov",
    author_email = "aquavitale@yandex.ru",
    description = "Yet another password store",
    license = "MIT",
    keywords = "yandexdisk onepassword crypt",
    url = "https://github.com/viert/yanpassword"
)
