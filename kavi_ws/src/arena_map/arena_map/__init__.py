"""Setup script for the arena_map ament_python package."""
import os
from glob import glob
from setuptools import setup

PACKAGE_NAME = 'arena_map'


def collect_data_files():
    """Install launch/maps/config/rviz resources under share/<pkg>/<sub>."""
    data = [
        ('share/ament_index/resource_index/packages',
            ['resource/' + PACKAGE_NAME]),
        (f'share/{PACKAGE_NAME}', ['package.xml']),
    ]
    for sub in ('maps', 'launch', 'config', 'rviz'):
        files = [p for p in glob(f'{sub}/*') if os.path.isfile(p)]
        data.append((f'share/{PACKAGE_NAME}/{sub}', files))
    return data


setup(
    name=PACKAGE_NAME,
    version='1.0.0',
    packages=[PACKAGE_NAME],
    data_files=collect_data_files(),
    install_requires=['setuptools'],
    zip_safe=True,
    author='user',
    author_email='user@todo.todo',
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='Static NAV2 occupancy map for the UK Lunabotics Arena '
                '(9m x 5m) with colored zone-overlay markers for RViz2.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'zone_markers = arena_map.zone_markers:main',
        ],
    },
)
