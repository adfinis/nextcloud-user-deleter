from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="nextcloud-user-deleter",
    version="0.0.1",
    description="Delete nextcloud Users",
    url="https://github.com/adfinis-sygroup/nextcloud-user-deleter",
    author="Adfinis SyGroup",
    license="AGPL-3.0",
    packages=["nextcloud_user_deleter"],
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        "console_scripts": ["nextcloud-user-deleter=nextcloud_user_deleter.app:main"]
    },
    data_files=[
        ('/usr/lib/systemd/system',
            ['config/nextcloud-user-deleter.service',
             'config/nextcloud-user-deleter.timer']
        ),
    ]
)
