from parameterized import param

DEPLOY_SCENARIOS = [
    (
        False,
        {'service':'AcmeService', 'version':'3.1.1', 'env':'production'},
        {'mode':'overwrite'}
    ),
    (
        False,
        {'service':'FunTimesService', 'version':'4.1.4', 'env':'staging', 'slice':'blue'},
        {'mode':'bg'}
    ),
    (
        False,
        {'service':'AcmeService', 'version':'3.1.1', 'env':'production', 'slice':'green'},
        {'mode':'bg'}
    ),
    (
        True,
        {'service':'AcmeService', 'version':'3.1.1', 'env':'production'},
        {'mode':'overwrite'}
    ),
    (
        True,
        {'service':'FunTimesService', 'version':'4.1.4', 'env':'staging', 'slice':'blue'},
        {'mode':'bg'}
    ),
    (
        True,
        {'service':'AcmeService', 'version':'3.1.1', 'env':'production', 'slice':'green'},
        {'mode':'bg'}
    )        
]
