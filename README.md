# Kubernetes Deployment Builder for EBBS
This script allows you to build `deployment` projects.
Essentially, this is an alternative to [Helm templates](https://helm.sh/docs/chart_best_practices/templates/). The goal is to use Python and the [Eons Library](https://github.com/eons-dev/eons.lib) to provide a more powerful and more intuitive templating system. This Builder also uses the [Eons Infrastructure Technologies](https://infrastructure.tech) package repository in place of a [Helm chart repo](https://helm.sh/docs/topics/chart_repository/).

## Output
This Builder compiles all `*.yaml` files in the `src` folder, all dependencies in the `dep` folder, and all dependencies missing from `dep` that can be found online. It puts this compiled output into a single .yaml file, usually `out/compiled.yaml`.

It is recommended that you publish this output to the Infrastructure Technologies repo for use as a dependency in other deployments. This can be done with [publish.build](https://github.com/eons-dev/publish.build).

To install the generated chart, use the [deploy.merx](https://github.com/eons-dev/deploy.merx) through [EMI](https://github.com/eons-dev/emi.exe).

## Naming
Each source file will be placed in a yaml object of the file's base name (everything up to the first '.'. This acts similar to a namespace, and should be unnoticeable to you. However, should you need to specify configuration values later, you may do so by creating a yaml or json object of the file's name.  

For example, if you have something like `service: {name: ...}` in both a `mysql.yaml` and a `redis.yaml` file, you can set the `mysql.service.name` to address the service name used in mysql.yaml.

The same is true of dependencies: each dependency will be placed in it's own object based in the dependency name up to the first '.'.

## Options
* `"output_folder"` ("out") - where to put the generated file.
* `"output_file"` ("compiled.yaml") - the name of the single yaml file to generate.
* `"dependencies"` ([]) - an array of dependencies; for example `["my_dependency.deployment"]`; versions are not allowed at this time.
* `"dependencies_as` ({}) - a dictionary of dependencies and what they should be called (e.g. if you use the same dependency more than once).
