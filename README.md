<img alt="Data Pipeline Wind Tunnel" src="./docs/img/plantd.png" width=200>


## Data Pipeline PlantD
Performance and Latency ANalysis Testing for Data pipelines is a harness for measuring the performance of data pipelines during and after development. DPWT collects a standard suite of metrics and visualizations, for use when developing or deciding among data pipeline architectures, configurations, and business use cases.

## Getting Started

### Concepts
To use the PlantD, you configure it with the following information:
- How to reach your **pipeline-under-test**: a description of the pipeline you want to measure, including at least an IP address and port number to send data in, and tags that uniquely identify your pipeline's resources on your cloud provider.
- The **data schema** that your pipeline requires as input, that is, what data items are fed into the pipeline, as well as their data format and allowable values.  
	- From this, PlantD will generate a **dataset**: a quantity of generated fake data that meets that schema, for use in testing
- A **load pattern** describing a variable rate of load generation, for example: *100 records per second steadily for 5 minutes, then ramping up over 1 minute to 200 records per second, staying steady for 10 minutes, then ramping down to 0 over a 2 minute span.*
	- The PlantD's **load generator** will send data to your pipeline following this pattern
- A description of the **experiment** you want to run: a timed session where the *load generator* sends a *dataset* to a *pipeline-under-test* using a *load pattern*, and collects metrics during and after the load generation.

## Prerequisites

You will need:
- A pipeline to measure
- A Kubernetes Cluster (Managed or Standalone)
- kubectl with access to the cluster

### Test Pipeline (Coming soon)
If you aren't ready to test your own pipeline, we supply a toy pipeline for demonstration

### Kubernetes cluster
If you don't have a kubernetes cluster handy, you can setup a small test cluster using Minikube.

Note that this will not scale up well to measuring dataflow of large pipelines, but it's enough to experiment and find out how PlantD works.

Type `kubectl cluster-info` to check that it's running


## Deploying the Operator

#### Bundle deployments

	```
		### Instal the K6 Operator
		curl https://raw.githubusercontent.com/grafana/k6-operator/main/bundle.yaml | kubectl create -f -

		### Install the Prometheus Operator
		curl https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml | kubectl create -f -


		### Install the PlantD Operator
		curl https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml | kubectl create -f - 
	```

## Funding

Data Pipeline Wind Tunnel is funded by Honda's 99P labs, with implementation and ongoing support provided by the TEEL team at Carnegie Mellon University. 

## License

Data Pipeline Wind Tunnel is licensed under the GPLv2 License. See [LICENSE](LICENSE) for more details.

## Documentation

For more detailed information about how to use Data Pipeline Wind Tunnel, see our full [documentation](https://DataPipelineWindTunnel.github.io/docs).

## Contact

[<img alt="99p Labs" src="./docs/img/99P_Labs_Red_linear.png" width="200">](https://developer.99plabs.io/home/)
[<img alt="TEEL Lab logo" src="./docs/img/teel-logo.png" width="100">](https://teel.cs.cmu.edu)
[<img alt="Carnegie Mellon University" src="./docs/img/cmu-logo.png" width="100">](https://www.cmu.edu)

For more information about the Data Pipeline Wind Tunnel project, please contact us:

- Honda 99P labs: 99P-contact@honda.com
- TEEL Labs: some-email@cmu.edu

We are always open to collaboration, questions, and suggestions!
 
## Acknowledgments

We would like to thank all contributors, both from Honda and CMU, for their dedication and hard work on this project. 


## Contributing

For guidelines on how to contribute to this project, how to hack on PlantD, and
information about what we require from project contributors, please see
[CONTRIBUTING.md](CONTRIBUTING.md).