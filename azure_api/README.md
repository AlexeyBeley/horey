/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

```mkdir homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | \
tar xz --strip 1 -C homebrew```


export PATH=/Users/<your_name>/homebrew/bin:$PATH

brew update && brew install azure-cli


Taken from here: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-macos
export PATH=/Users/<your_name>/homebrew/bin:$PATH
az login #opens browser
az login --use-device-code

#Find available SKUs
az vm list-skus --location southcentralus --size Standard_F --all --output table

/usr/local/etc/bash_completion.d/

# az login --use-device-code
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code CF8G32UMG to authenticate.
[
  {
    "cloudName": "XXXXXXX",
    "homeTenantId": "XXXXXXX",
    "id": "XXXXXXX",
    "isDefault": true,
    "managedByTenants": [],
    "name": "XXXXXXX",
    "state": "Enabled",
    "tenantId": "XXXXXXX",
    "user": {
      "name": "XXXXXXX",
      "type": "user"
    }
  }

#az ad sp create-for-rbac --name localtest-sp-rbac --skip-assignment
#To retrieve your subscription ID, run the "az account show" command and look for the id property in the output.]

# ubuntu:
pip3 install setuptools_rust docker-compose
#did not work sudo apt-get install rustc -y
# sudo apt-get install libpcre3-dev -y
cryptography==3.0.0
pip3 install azure-identity

# macos
test:
3.4.7
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Warning:  is not in your PATH.
export PATH="/opt/homebrew/bin:$PATH"
brew install openssl


pip3 install setuptools_rust docker-compose
brew install rust
pip3 install azure-identity


az ad sp create-for-rbac --name osba -o table
AppId                                 DisplayName    Name         Password                            Tenant
------------------------------------  -------------  -----------  ----------------------------------  ------------------------------------
XXXXXXX  osba                         http://osba    XXXXXXX       XXXXXXX


ication request to the wrong tenant.
Trace ID: XXXXXXX
Correlation ID: XXXXXXX
Timestamp: 2021-05-09 17:13:34Z


"App registrations"
{
  "appId": "XXXXXXX",
  "displayName": "XXXXXXX",
  "name": "http://XXXXXXX",
  "password": "XXXXXXX",
  "tenant": "XXXXXXX"
}