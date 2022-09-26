def check_dependencies():

    import sagemaker
    
    import sys
    import os
    import IPython

    def versiontuple(v):
        return tuple(map(int, (v.split("."))))
    
    kernel_restart_required = False
    
    required_version = '2.90.0'
    if (versiontuple(sagemaker.__version__) < versiontuple(required_version)): 
        print('This workshop was tested with sagemaker version {} but you are using {}. Installing required version...'.format(required_version, sagemaker.__version__) )
        stream = os.popen('{} -m pip install -U sagemaker=={}'.format(sys.executable, required_version))
        output = stream.read()
        print(output)
        kernel_restart_required = True
    
    if kernel_restart_required:
        print("Restarting kernel after installing new dependencies...")
        IPython.Application.instance().kernel.do_shutdown(True)     
        print('WARNING: Kernel restarting...please wait 30 seconds before moving to the next cell!')