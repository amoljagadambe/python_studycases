Kermit
-------

Kermit Module 

Install
-------
## clone the repository
    git clone git@bitbucket.org:pti-development-team/kermit.gitt
    # checkout the correct branch
    git fetch && git checkout feature/AED-22-testing-with-pytest---unit-testin
    
Create a virtualenv in the kermit directory and activate it(3.8)::

    python -m venv venv
    venv\Scripts\activate.bat
    
Install Dependencies in Virtual Environment::

    pip install -r requirement.txt
    
 RUN
 ---
 
 NOTE: Before running the module please generate synthetic data for kermit module 
 
 On Virtual Environment::
    
    set PYTHONPATH=. (in unix use export)
    python commands/batch_run.py -s "2020-04-02 07:49:02" -e "2020-04-02 07:49:02" -i "yes" --is-local
    
HELP
----
-s : Start Time\
-e : End Time\
-i : Is-indexed\
--is-local: setting this parameter will look for .env file for configuration
