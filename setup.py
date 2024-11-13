from setuptools import setup

APP = ['scheduler.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['MetaTrader5', 'pandas', 'numpy', 'APScheduler'],  # Manually include a package
    # 'excludes': ['unnecessary_module'],  # Exclude a module that was detected but isn't needed
    'includes': ['algo', 'server'],  # Ensure an important module is included
    # 'resources': ['datafile.txt'],  # Include additional resources like data files
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
