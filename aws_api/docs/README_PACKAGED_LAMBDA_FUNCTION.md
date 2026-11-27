# AWS_API configuration

###Basic example steps
package_directory:
    setup.py
    requirements.txt
    lambda_handler.py


export PACKAGE_SRC_DIRECTORY_PATH
export LAMBDA_NAME
make upload_packaged_lambda_function 

An option in setup.py I used to recognize the environment
python_requires='>=3',
https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires