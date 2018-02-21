from setuptools import setup, find_packages

from tools.distutils.command import bdist_cinema4d_plugin, rsync_cinema4d_plugin

setup(
    name='Py-Previz',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.2.0',
    description='Cinema4D Previz plugin',
    url='https://app.previz.co',
    author='Previz',
    author_email='info@previz.co',
    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2 :: Only'
        'Programming Language :: Python :: 2.6',
    ],

    keywords='previz 3d scene exporter',
    packages=find_packages(exclude=['tools*']),
    install_requires=['previz'],
    extras_require={},
    package_data={},
    data_files=[],
    cmdclass={
        'bdist_cinema4d_plugin': bdist_cinema4d_plugin,
        'rsync_cinema4d_plugin': rsync_cinema4d_plugin
    }
)
