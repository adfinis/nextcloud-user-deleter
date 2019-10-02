from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="nextcloud-user-cleanup",
    version="0.0.1",
    description="Delete nextcloud Users",
    url="https://github.com/adfinis-sygroup/nextcloud-user-cleanup",
    author="Adfinis SyGroup",
    license="AGPL-3.0",
    packages=["nextcloud_user_cleanup"],
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        "console_scripts": ["nextcloud-user-cleanup=nextcloud_user_cleanup.app:main"]
    },
    data_files=[
        ('/usr/lib/systemd/system',
            ['config/nextcloud-user-cleanup.service'],
            ['config/nextcloud-user-cleanup.timer']
        ),
    ]
)
