import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-school-hr-manpower",
    description="Meta package for open-synergy-ssi-school-hr-manpower Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_hr_manpower_planning_school',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
