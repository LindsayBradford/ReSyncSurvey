# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/deploy.py  - deploys only the runtime python scripts.
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

import os
import shutil

class Deployer():

    def __init__(self):
        self._source_files = [
            'ReSyncSurvey.py', 'support',
            'ReSyncSurvey.atbx',
            'config_file_template.ini',
            'README.md'
        ]
        self._target_folder =  os.path.join(os.getcwd(),'deploy')

    def deleteDeployFolderContent(self):
        for filename in os.listdir(self._target_folder):
            file_path = os.path.join(self._target_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def setupDeployFolder(self):
        print(f'Setting up deploy folder [{self._target_folder}]...')
        if not os.path.exists(self._target_folder):
            print(f'  Deploy folder does not exist. Creating...')
            os.makedirs(self._target_folder)
        else:
            print(f'  Deleting content of deploy folder...')
            self.deleteDeployFolderContent()    

    def isPythonModule(self, path):
        split_path = os.path.splitext(path)
        if split_path[1] == '.py':
            return True
        return False

    def copyFilesToDeployFolder(self):
        print(f'Copying files to [{self._target_folder}]...')

        for sourceFile in self._source_files:
            if os.path.isfile(sourceFile):
                self.copyFile(sourceFile)
            if os.path.isdir(sourceFile):
               self.copyModuleFolder(sourceFile)
    
    def copyFile(self, sourceFile):
        destinationFile = os.path.join(self._target_folder, sourceFile)
        shutil.copy(sourceFile, destinationFile)
        
    def copyModuleFolder(self, source_folder):
        destination_folder = os.path.join(self._target_folder, source_folder)
        os.makedirs(destination_folder)

        for filename in os.listdir(source_folder):
            self.copyPythonModule(filename, source_folder, destination_folder)
                
    def copyPythonModule(self, filename, source_folder, destination_folder):
        file_path = os.path.join(source_folder, filename)
        if not self.isPythonModule(file_path):
            return

        destination_module = os.path.join(destination_folder, filename)
        shutil.copy(file_path, destination_module)

    def deploy(self):
        self.setupDeployFolder()
        self.copyFilesToDeployFolder()


if __name__ == '__main__':     
    Deployer().deploy()
