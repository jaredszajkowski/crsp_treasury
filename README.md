CRSP Treasury
=============


## Quick Start

### Step 0: Clone Repository

*Self-Signed Certificate Errors with OFR BitBucket Instance*:
To clone this repository or others from the OFR Bitbucket, you might have trouble with self-signed certificates. You can disable this for the cloning action as follows:
```
git -c http.sslVerify=false clone https://repository.ofr.treas.gov/scm/~jbejarano/project_template.git
```
If you have trouble pushing your changes, you can add this flag to the push as well. For example, use
```
git -c http.sslVerify=false push origin main
```

### Step 1: Set Up SSH Connections

You will also need to set up an SSH key and a keytab file. You can set up the SSH key like this. After connecting via SSH to `grid.ofr.treas.gov`, just paste the following lines into the OFR Grid terminal:
```
rm -irf ~/.ssh/authorized_keys
## accept all the defaults, leave the password blank
yes | ssh-keygen -t ecdsa -b 521 -N "" -f ~/.ssh/id_ecdsa 
cat ~/.ssh/id_ecdsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
## Now, ssh into trino.emr.ofr.treas.gov. It should not ask you for a password
ssh -o "StrictHostKeyChecking=accept-new" -t trino.emr.ofr.treas.gov 'printf "\n\nTrino connection setup completed successfully\n\n"'

```
Now, you should also do this in the Windows Command Prompt, so you can ssh into the grid without a password. Just copy the following lines into Windows Command Prompt:
```
del %USERPROFILE%\.ssh\id_rsa*
ssh-keygen -t rsa -b 2048 -f "%USERPROFILE%\.ssh\id_rsa" -N ""
type %USERPROFILE%\.ssh\id_rsa.pub >> U:\.ssh\authorized_keys
:: Sleep for 5 seconds to allow time to sync files
ping 127.0.0.1 -n 6 > nul
:: type "%USERPROFILE%\.ssh\id_rsa.pub" | ssh grid.ofr.treas.gov "cat >> ~/.ssh/authorized_keys"
ssh -o "StrictHostKeyChecking=accept-new" -t grid.ofr.treas.gov echo -e "\\n\\nGrid connection setup completed successfully\\n\\n"
```

You can create the keytab file using the 
[directions here](https://confluence.ofr.treas.gov/display/APPDEV/How+to+create+a+Kerberos+Keytab+file). Use the default settings given in the instructions.
It is preferred, but not required that you save the keytab file in your user directory and name it using your username. Thus, if your username is `jdoe`, it would be saved here:
```
/data/unixhome/jdoe/jdoe.keytab
```

### Step 2: Connect to OFR Grid via SSH

Next, connect to the OFR grid using the following instructions.
Although most of this code is platform independent, a limited few aspects of this repo will only work on the OFR grid 
(e.g., because it's running SQL pulls from our Trino database).
A limited few of them will only work there. This code is designed to be run from the command line after connecting via SSH. 
For interactive work, my preferred workflow follows these steps described 
[here.](https://confluence.ofr.treas.gov/pages/viewpage.action?spaceKey=OFRSYS&title=RAC%27s+Guide+to+Using+OFR%27s+HPC+Systems#RAC'sGuidetoUsingOFR'sHPCSystems-UseJupyterNotebookinLocalVDIwithJupyterserverrunningonworkernode)

For convenience, I repeat the main steps of this interactive work here:
```
ssh grid
tmux ## use this to prevent disconnection
cd /data/
module use -a /opt/aws_ofropt/Ubuntu_Modulefiles
module load anaconda3/3.11.4 TeXLive/2023 R/4.4.0 stata/17
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
pip install -r requirements.txt ## only needs to be done once. You may optionally use venv below
salloc --exclusive srun -X --pty bash -c 'jupyter notebook --no-browser --ip=$SLURMD_NODENAME' 
```
In a separate, local instance of Command Prompt, run this (subbing in the name
of the checked out node from above)
```
ssh grid.ofr.treas.gov -L 8888:defq-dy-generalq-6:8888 -N 
```

### Step 3: Configure environment variables in `.env` 

This template uses a `.env` file to contain user-specific configurations and secrets (such as API keys). The purpose is to separate configuration from code. This project uses the `decouple` [Python package](https://pypi.org/project/python-decouple/).

Create a new file called `.env` and save it in the root project directory. 
This files should NOT be committed to Git, since it can contain private
information. Use the included file `env.example` to
give you a sense of what the `.env` file should look like.
Include your user-specific and other configurations in this file.
Some examples would be to include your OFR username and the path
to your keytab file:

```
KEYTAB=config("KEYTAB", default="") ## Path to keytab file, 
## e.g. "/data/unixhome/jdoe/jdoe.keytab"
```


### Step 4: Install required software on grid

**LaTeX**
The reports of this code use LaTeX. 
You must have TexLive (or another LaTeX distribution) installed on your computer and available in your path.
I strongly recommend TeXLive, since it contains a snapshot of all available packages and you don't have to deal
with LaTeX package management (which is troublesome because of OFR restrictions). TeXLive can be obtained via 
a UAR. It can alternatively be loaded on the grid with the `module` command. More on that below.

**Conda or another environment manager**
To run this code, I recommend only using `conda` for the bare minimum. This is because `conda` is too slow
and `mamba` in not currently available on the OFR grid. Thus, for managing environments and Python versions, I use `conda`. 
For all other package management, I recommend `pip`.

**Working on the Grid**
On the grid, the easiest way to get started is to simply load Anaconda and TexLive modules.
You can do this with 
```
module use -a /opt/aws_ofropt/Modulefiles
module load anaconda3/3.11.4 TeXLive/2023 R/4.4.0 pandoc/3.1.6 gcc/14.1.0 stata/17
```
You need to do this with every new session. The alternative is to install these yourself.
Now, you have an optional step of creating a virtual environment (for package isolation):
```
python -m venv ~/.venvs/pipeline
source ~/.venvs/pipeline/bin/activate ## Note: use deactivate to undo
```
Note, in Windows the command is `venv\Scripts\activate` and `deactivate`.

Having done this, then install the dependencies with pip (only needs to be done once)
```
pip install -r requirements.txt
```
Finally, you can then run 
```
doit
```
And that's it!

**Alternative Using Conda (which can be tricky on the grid)**

Having installed LaTeX and conda, open a terminal and navigate to the root directory of the project and create a 
conda environment using the following command:
```
conda create -n blank python=3.12
conda activate blank
```
and then install the dependencies with pip
```
pip install -r requirements.txt
```
Finally, you can then run 
```
doit
```
And that's it!

### Step 5: Optional Usage of R

If you would also like to run the R code included in this project, you can either install
R and the required packages manually. The included `environment.yml` file
contains the R packages needed, but these are unavailable through the OFR's conda channel.


## Other commands

rsync -lr --delete --exclude={.venv,_output,_data,.git} /data/Analytics/collaboration/collab_nccbr/alt_base/alt_base/pipelines/NCCBR/ /data/unixhome/jbejarano/GitRepositories/altbase/pipelines/NCCBR/

### Copying Project Template Code without .git subdirectory

Copying from one folder to another, using absolute paths. Rename the folder along the way to "mypipeline":
```
rsync -lrv --delete --exclude={.venv,_output,_data,.git} /data/Department_Shares/Researchers/jbejarano/_pipeline_template/ /data/Department_Shares/Researchers/jbejarano/chart_base_demo/mypipeline/
```

I use the following to copy from my personal copy of the repo to a shared version in the "Researchers" directory. It will delete
any files present in the destination that are not in the source.
```
rsync -lrv --delete --exclude={.venv,_output,_data,.git} ./ /data/Department_Shares/Researchers/jbejarano/_pipeline_template/
```
mkdir -p /ofrScratch/$USER/_pipeline_template/
chmod 700 /ofrScratch/$USER/_pipeline_template/
rsync -lr --delete --exclude={.venv,_output,_data,_docs,.git} ./ /ofrScratch/$USER/_pipeline_template/

### Unit Tests and Doc Tests

You can run the unit test, including doctests, with the following command:
```
pytest --doctest-modules
```
You can build the documentation with:
```
rm ./src/.pytest_cache/README.md 
jupyter-book build -W ./
```
Use `del` instead of rm on Windows

## Dependencies and Virtual Environments

### Working with `pip` requirements

`conda` allows for a lot of flexibility, but can often be slow. `pip`, however, is fast for what it does.  You can install the requirements for this project using the `requirements.txt` file specified here. Do this with the following command:
```
pip install -r requirements.txt
```

The requirements file can be created like this:
```
pip list --format=freeze
```

### Working with `conda` environments

The dependencies used in this environment (along with many other environments commonly used in data science) are stored in the conda environment called `blank` which is saved in the file called `environment.yml`. To create the environment from the file (as a prerequisite to loading the environment), use the following command:

```
conda env create -f environment.yml
```

Now, to load the environment, use

```
conda activate blank
```

Note that an environment file can be created with the following command:

```
conda env export > environment.yml
```

However, it's often preferable to create an environment file manually, as was done with the file in this project.

Also, these dependencies are also saved in `requirements.txt` for those that would rather use pip. Also, GitHub actions work better with pip, so it's nice to also have the dependencies listed here. This file is created with the following command:

```
pip freeze > requirements.txt
```

**Other helpful `conda` commands**

- Create conda environment from file: `conda env create -f environment.yml`
- Activate environment for this project: `conda activate blank`
- Remove conda environment: `conda remove --name blank --all`
- Create blank conda environment: `conda create --name myenv --no-default-packages`
- Create blank conda environment with different version of Python: `conda create --name myenv --no-default-packages python` Note that the addition of "python" will install the most up-to-date version of Python. Without this, it may use the system version of Python, which will likely have some packages installed already.
