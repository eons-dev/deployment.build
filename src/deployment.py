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

        this.optionalKWArgs["description"] = "Helm chart of some kind"
        this.optionalKWArgs["version"] = "0.0.0"
        this.optionalKWArgs["library_output_folder"] = "lib"
        this.optionalKWArgs["helm_output_folder"] = "helm"
        this.optionalKWArgs["output_file"] = "compiled.yaml"
        this.optionalKWArgs["dependencies"] = []
        this.optionalKWArgs["api_version"] = "v2"
        this.optionalKWArgs["chart_type"] = "application"
        this.optionalKWArgs["chart_additional"] = ""

        this.supportedProjectTypes = [
            "deployment"
        ]

    # Required Builder method. See that class for details.
    def DidBuildSucceed(this):
        results = [this.library_output_folder, this.helm_output_folder]
        logging.debug(f"Checking if build was successful; output should be in {results}")
        return all([os.listdir(res) for res in results])

    # Required Builder method. See that class for details.
    def Build(this):
        this.MeetDependencies()
        this.Compile()
        this.WriteMeta()

    # Write all the files necessary to make this a helm chart.
    def WriteMeta(this):
        chart = this.CreateFile(Path(this.helm_output_folder).joinpath("Chart.yaml"))
        chart.write(f'''\
apiVersion: {this.api_version}
name: {this.projectName}
description: {this.description}

# A chart can be either an 'application' or a 'library' chart.
#
# Application charts are a collection of templates that can be packaged into versioned archives
# to be deployed.
#
# Library charts provide useful utilities or functions for the chart developer. They're included as
# a dependency of application charts to inject those utilities and functions into the rendering
# pipeline. Library charts do not define any templates and therefore cannot be deployed.
type: {this.chart_type}

# This is the chart version. This version number should be incremented each time you make changes
# to the chart and its templates, including the app version.
# Versions are expected to follow Semantic Versioning (https://semver.org/)
version: {this.version}

# This is the version number of the application being deployed. This version number should be
# incremented each time you make changes to the application. Versions are not expected to
# follow Semantic Versioning. They should reflect the version the application is using.
appVersion: {this.version}

{this.chart_additional}
''')
        chart.close()

        ignore = this.CreateFile(Path(this.helm_output_folder).joinpath(".helmignore"))
        ignore.write(f'''\
# Patterns to ignore when building packages.
# This supports shell glob matching, relative path matching, and
# negation (prefixed with !). Only one pattern per line.
.DS_Store
# Common VCS dirs
.git/
.gitignore
.bzr/
.bzrignore
.hg/
.hgignore
.svn/
# Common backup files
*.swp
*.bak
*.tmp
*.orig
*~
# Various IDEs
.project
.idea/
*.tmproj
.vscode/
''')
        ignore.close()

        values = this.CreateFile(Path(this.helm_output_folder).joinpath("values.yaml"))
        # We don't use the values file.
        values.close()


    # Download all packages the project depends on and extract them to this.depPath
    def MeetDependencies(this):
        # Hack the repo.store in order to save dependencies to the depPath
        if (not this.originalRepoStore):
            this.originalRepoStore = this.executor.repo.store
            this.executor.repo.store = this.depPath
        
        for dep in this.dependencies:
            depPath = Path(this.depPath).joinpath(f"{dep}")
            if (not depPath.exists()):
                this.executor.DownloadPackage(dep, registerClasses = False, createSubDirectory = True)
        
        this.executor.repo.store = this.originalRepoStore
        this.originalRepoStore = None


    # Ingest all the source yaml files and write them to one big, compiled yaml file.
    def Compile(this):
        this.libFile = this.CreateFile(Path(this.library_output_folder).joinpath("templates").joinpath(this.output_file))
        this.helmFile = this.CreateFile(Path(this.helm_output_folder).joinpath("templates").joinpath(this.output_file))

        locs = [f"{this.depPath}/{dep}" for dep in this.dependencies]
        locs.append(this.srcPath)
        for loc in locs:
            for file in glob.glob(f"{loc}/*.yaml"):
                logging.debug(f"Ingesting {file}")
                iFile = open(Path(file), 'r')
                for line in iFile:
                        this.libFile.write(line)
                    try:
                        this.helmFile.write(eval(f"f\"{line[:-1]}\""))
                        this.helmFile.write("\n")
                    except Exception as e:
                        logging.error(str(e))

                this.libFile.write('---\n')
                this.helmFile.write('---\n')
                iFile.close()
        
        this.libFile.close()
        this.helmFile.close()
