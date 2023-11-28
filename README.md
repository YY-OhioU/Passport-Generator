# Passport Generation
## How to Use
### Install libraries
`pip install -r requirements.txt`
### Modify installed 'PILasOPENCV' package
1. Locate `site-packages`folder in your python environment
2. Under `site-packages`, find `PILasOPENCV.py`
3. Change all `np.bool` to `np.bool_` (Three happenings at line 533, 607, 2079)

### Run code
`python main.py`