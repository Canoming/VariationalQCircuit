from setuptools import setup

setup(name='variational_circuit',
      version='0.3',
      description='QuTip based variational circuit',
      url='https://github.com/Canoming/VariationalQCircuit',
      author='Canoming',
      author_email='canoming@163.com',
      license='MIT',
      packages=['variational_circuit'],
      install_requires=[
          'numpy',
          'scipy',
          'qutip',
          'bitstring',
      ],
      zip_safe=False)