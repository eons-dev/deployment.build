import os
import logging
from glob import glob
from pathlib import Path
from ebbs import Builder
from ebbs import OtherBuildError

# Class name is what is used at cli, so we defy convention here in favor of ease-of-use.
class deployment(Builder):
    def __init__(this, name="Kubernetes Deployment Builder"):
        super().__init__(name)

        this.optionalKWArgs["output_folder"] = "out"
        this.optionalKWArgs["output_file"] = "compiled.yaml"
        this.optionalKWArgs["dependencies"] = []
        this.optionalKWArgs["dependencies_as"] = {}

        this.supportedProjectTypes = [
            "deployment"
        ]

        this.originalRepoStore = None

    # Required Builder method. See that class for details.
    def DidBuildSucceed(this):
        results = [this.output_folder] # list in case we want to compile to multiple outputs.
        logging.debug(f"Checking if build was successful; output should be in {results}")
        return all([os.listdir(res) for res in results])

    # Required Builder method. See that class for details.
    def Build(this):
        this.MeetDependencies()
        this.Compile()

    # Download all packages the project depends on and extract them to this.depPath
    def MeetDependencies(this):
        # Hack the repo.store in order to save dependencies to the depPath
        if (not this.originalRepoStore):
            this.originalRepoStore = this.executor.repo.store
            this.executor.repo.store = this.depPath
        
        for dep, dest in this.dependencies_as:
            destPath = Path(this.depPath).joinpath(f"{dest}")
            tmpPath = Path(this.depPath).joinpath(f"{dep}")
            if (destPath.exists()):
                continue
            if (tmpPath.exists()):
                raise Exception(f"Cannot download {dep} to {tmpPath}")
            this.executor.DownloadPackage(dep, registerClasses = False, createSubDirectory = True)
            tmpPath.rename(destPath)

        for dep in this.dependencies:
            depPath = Path(this.depPath).joinpath(f"{dep}")
            if (depPath.exists()):
                continue
            this.executor.DownloadPackage(dep, registerClasses = False, createSubDirectory = True)
        
        this.executor.repo.store = this.originalRepoStore
        this.originalRepoStore = None


    # Ingest all the source yaml files and write them to one big, compiled yaml file.
    def Compile(this):
        this.outFile = this.CreateFile(Path(this.output_folder).joinpath(this.output_file))

        locs = [f"{this.depPath}/{dep}" for dep in this.dependencies]
        locs.append(this.srcPath)
        for loc in locs:
            if (loc != this.srcPath):
                locContextKey = loc.split('/')[-1].split('.')[0]
                this.outFile.write(f"{{this.executor.PushGlobalContextKey('{locContextKey}')}}\n")
            
            for file in glob(f"{loc}/*.yaml"):
                
                # File context is a little too specific.
                # Configs can be referenced by deployment name for now.
                #
                # fileContextKey = file.split('/')[-1].split('.')[0]
                # this.outFile.write(f"{{this.executor.PushGlobalContextKey('{fileContextKey}')}}\n")

                logging.debug(f"Ingesting {file}")
                iFile = open(Path(file), 'r')
                for line in iFile:
                    try:
                        this.outFile.write(line)
                    except Exception as e:
                        logging.error(str(e))
                iFile.close()

                # this.outFile.write(f"{{this.executor.PopGlobalContextKey('{fileContextKey}')}}\n")
                this.outFile.write('\n---\n')

            if (loc != this.srcPath):
                this.outFile.write(f"{{this.executor.PopGlobalContextKey('{locContextKey}')}}\n")
        
        this.outFile.close()
