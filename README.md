# trellomize
the simple project for managing projects and tasks

### Requirements
<code>git clone https://github.com/alirezarezaei1/trellomize.git </code> 
#### Linux: 
with pipx: <br>
<code> sudo apt install pipx </code>
<br>
<code> pipx install poetry </code>
<br>
<code> poetry install </code>
<br>
with curl: <br>
<code> curl -sSL https://install.python-poetry.org | python3 - </code>
<br>
<code> poetry install </code>
<br>

#### Windows:
<code> curl -sSL https://install.python-poetry.org | python3 - </code>
<br>
<code> poetry install </code>
<br>

### Run
<code> poetry shell </code>
<br>
<code> python main.py </code>

### Create Admin
<code> python manager.py create-admin --username ${username} --password ${password} </code>

### Remove all data
<code> python manager.py purge-date </code>
