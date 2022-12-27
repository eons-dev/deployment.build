# Kubernetes Deployment Builder for EBBS
This script allows you to build `deployment` projects.
Essentially, this is an alternative to [Helm templates](https://helm.sh/docs/chart_best_practices/templates/). The goal is to use Python and the [Eons Library](https://github.com/eons-dev/eons.lib) to provide a more powerful and more intuitive templating system. This Builder also uses the [Eons Infrastructure Technologies](https://infrastructure.tech) package repository in place of a [Helm chart repo](https://helm.sh/docs/topics/chart_repository/).

## Output
This Builder compiles all `*.yaml` files in the `src` folder, all dependencies in the `dep` folder, and all dependencies missing from `dep` that can be found online. It puts this compiled output into 2 separate .yaml files:
1. Library: a compiled but uninterpreted file for use as a dependency in other deployments (i.e. no value substitution).
2. Helm: a compiled and interpreted file which it then wraps in a Helm chart for use in k8s (i.e. with value substitution).

It is recommended that you publish the first output, the "library" to the Infrastructure Technologies repo. This can be done with [publish.build](https://github.com/eons-dev/publish.build).

While this Builder offers an alternative to Helm in many ways, in the end, it outputs a Helm chart. This is done both to make deployment within Kubernetes easier and to enable compatibility with existing Helm charts.

However, if you'd like to bypass Helm altogether, just `kubectl apply -f helm/templates/compiled.yaml`.

## Options
* `"description"` ("Helm chart of some kind") - chart description.
* `"version"` ("0.0.0") - version for both version and appVersion.
* `"library_output_folder"` ("lib") - where to put the compiled but unsubstituted yaml file.
* `"helm_output_folder"` ("helm") - where to put the generated helm chart.
* `"output_file"` ("compiled.yaml") - the name of the single yaml file to generate.
* `"dependencies"` ([]) - an array of dependencies; for example `["my_dependency.deployment"]`.
* `"api_version"` ("v2") - See [the Helm docs](https://helm.sh/docs/topics/charts/#the-apiversion-field).
* `"chart_type"` ("application") - See [the Helm docs](https://helm.sh/docs/topics/charts/#chart-types).
* `"chart_additional"` ("") - anything extra to add to `Chart.yaml`; note that if you're setting this in json, double escape your newlines (`\\n`).