from setuptools import setup,find_packages

setup(name='variational_circuit',
      version='0.4',
      description='QuTip based variational circuit',
      url='https://github.com/Canoming/VariationalQCircuit',
      author='Canoming',
      author_email='canoming@163.com',
      license='MIT',
      packages=find_packages(exclude=["*.tests","*.tests.*","tests.*","tests"]),
      install_requires=[
          'numpy',
          'scipy',
          'qutip',
      ],
      zip_safe=False)