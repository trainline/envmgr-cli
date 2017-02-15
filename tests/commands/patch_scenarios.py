    
from nose_parameterized import param

LATEST_STABLE_WINDOWS_APP = 'windows-2012r2-app-7.3.2'
LATEST_STABLE_WINDOWS_SECURE = 'windows-2012r2-secureapp-7.3.0'
LATEST_STABLE_UBUNTU = 'ubuntu-16.04-0.2.7'
WINDOWS_SECURE_7_0_0 = 'windows-2012r2-secureapp-7.0.0'
WINDOWS_SECURE_5_5_3 = 'windows-2012r2-secureapp-5.5.3'

TEST_SCENARIOS=[
    param( # Mix of latest Windows, old Windows and Linux
        {'n':5, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'A-team'}, 
        {'n':10, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'A-team'}, 
        {'n':7, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'A-team'}, 
        patch_cluster='A-team',
        expected=5
    ),
    param( # Large mixed set of latest Widows, old Windows and Linux
        {'n':5000, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'A-team'}, 
        {'n':10000, 'ami':LATEST_STABLE_WINDOWS_APP, 'latest':True, 'cluster':'A-team'}, 
        {'n':7000, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'A-team'}, 
        patch_cluster='A-team',
        expected=5000
    ),
    param( # Only old Windows
        {'n':87, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'A-team'}, 
        patch_cluster='A-team',
        expected=87
    ),
    param( # 2 different versions of old Windows
        {'n':10, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'A-team'}, 
        {'n':11, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'A-team'}, 
        {'n':16, 'ami':WINDOWS_SECURE_5_5_3, 'latest':False, 'cluster':'A-team'}, 
        {'n':7, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'A-team'}, 
        patch_cluster='A-team',
        expected=27
    ), 
    param( # Mutliple clusters, multiple versions
        {'n':19, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'B-team'}, 
        {'n':8, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'C-team'}, 
        {'n':21, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'D-team'}, 
        {'n':17, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'E-team'}, 
        {'n':45, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'A-team'}, 
        {'n':36, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'B-team'}, 
        {'n':11, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'C-team'}, 
        {'n':11, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'D-team'}, 
        {'n':4, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'E-team'}, 
        {'n':24, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'F-team'}, 
        {'n':9, 'ami':WINDOWS_SECURE_5_5_3, 'latest':False, 'cluster':'A-team'}, 
        {'n':1, 'ami':WINDOWS_SECURE_5_5_3, 'latest':False, 'cluster':'B-team'}, 
        {'n':8, 'ami':WINDOWS_SECURE_5_5_3, 'latest':False, 'cluster':'C-team'}, 
        {'n':6, 'ami':WINDOWS_SECURE_5_5_3, 'latest':False, 'cluster':'D-team'}, 
        {'n':7, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'A-team'}, 
        {'n':12, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'B-team'}, 
        {'n':28, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'X-team'}, 
        {'n':70, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'Q-team'}, 
        {'n':3, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'D-team'}, 
        patch_cluster='B-team',
        expected=37
    ), 
    param( # No servers belonging to queried cluster
        {'n':5, 'ami':WINDOWS_SECURE_7_0_0, 'latest':False, 'cluster':'A-team'}, 
        {'n':10, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'A-team'}, 
        {'n':7, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'A-team'}, 
        patch_cluster='B-team',
        expected=0
    ),
    param( # All servers are up to date
        {'n':15, 'ami':LATEST_STABLE_WINDOWS_SECURE, 'latest':True, 'cluster':'A-team'}, 
        {'n':9, 'ami':LATEST_STABLE_UBUNTU, 'latest':True, 'cluster':'A-team'}, 
        patch_cluster='A-team',
        expected=0
    ),
    param( # No Servers
        patch_cluster='A-team',
        expected=0
    ),
]

